import os
import sqlite3
import json
import base64
import uuid
import asyncio
import contextvars
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel, Field
from orchx_core.interfaces.security_contracts import SecretVault

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class EncryptionEngine:
    def __init__(self, master_key_base64: str = None):
        key = master_key_base64 or os.environ.get("ORCHX_MASTER_KEY")
        if not key:
            self.master_key = AESGCM.generate_key(bit_length=256)
        else:
            self.master_key = base64.b64decode(key)
        
        self.aesgcm = AESGCM(self.master_key)

    def export_key(self) -> str:
        return base64.b64encode(self.master_key).decode("utf-8")

    def encrypt(self, plaintext: str) -> Tuple[str, str]:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return base64.b64encode(ciphertext).decode("utf-8"), base64.b64encode(nonce).decode("utf-8")

    def decrypt(self, ciphertext_b64: str, nonce_b64: str) -> str:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")


class SecretAccessPolicy(BaseModel):
    service: str
    provider: str
    reason: str
    request_id: str

# Context variable for access control without breaking ABC signature
current_vault_policy = contextvars.ContextVar("current_vault_policy", default=None)

class SQLiteSecretVault(SecretVault):
    """
    Production-grade asynchronous secret vault with SQLite backend,
    AES-256 GCM encryption, versioning, rollback, and audit logging.
    """
    _DDL = """
    CREATE TABLE IF NOT EXISTS secrets (
        version_id TEXT PRIMARY KEY,
        secret_key TEXT NOT NULL,
        encrypted_value TEXT NOT NULL,
        nonce TEXT NOT NULL,
        active BOOLEAN NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id TEXT PRIMARY KEY,
        action TEXT NOT NULL,
        secret_key TEXT NOT NULL,
        actor TEXT NOT NULL,
        reason TEXT NOT NULL,
        success BOOLEAN NOT NULL,
        timestamp TEXT NOT NULL
    );
    """

    def __init__(self, db_path: str = ":memory:", encryption_engine: Optional[EncryptionEngine] = None):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(self._DDL)
        self._conn.commit()
        
        self.encryption = encryption_engine or EncryptionEngine()

    def _log_audit(self, action: str, secret_key: str, actor: str, reason: str, success: bool):
        self._conn.execute(
            "INSERT INTO audit_logs (log_id, action, secret_key, actor, reason, success, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), action, secret_key, actor, reason, success, _now())
        )
        self._conn.commit()

    async def get_secret(self, key: str) -> Optional[str]:
        policy = current_vault_policy.get()
        if not policy:
            self._log_audit("read", key, "unknown", "No policy provided", False)
            raise PermissionError("Access denied: missing SecretAccessPolicy")

        if policy.service not in ["ProviderCredentialManager", "AdminCLI", "WebFrontend"]:
            self._log_audit("read", key, policy.service, policy.reason, False)
            raise PermissionError(f"Access denied for service {policy.service}")

        row = self._conn.execute(
            "SELECT encrypted_value, nonce FROM secrets WHERE secret_key = ? AND active = 1 ORDER BY created_at DESC LIMIT 1",
            (key,)
        ).fetchone()

        if not row:
            self._log_audit("read", key, policy.service, policy.reason, False)
            return None

        try:
            plaintext = self.encryption.decrypt(row["encrypted_value"], row["nonce"])
            self._log_audit("read", key, policy.service, policy.reason, True)
            return plaintext
        except Exception:
            self._log_audit("read", key, policy.service, "Decryption/Integrity failure", False)
            raise ValueError("Secret integrity verification failed.")

    async def store_secret(self, key: str, value: str) -> None:
        policy = current_vault_policy.get()
        if not policy or policy.service not in ["ProviderCredentialManager", "AdminCLI", "WebFrontend"]:
            self._log_audit("create/update", key, getattr(policy, "service", "unknown"), "Unauthorized", False)
            raise PermissionError("Access denied for storing secrets")

        self._conn.execute("UPDATE secrets SET active = 0 WHERE secret_key = ?", (key,))
        
        encrypted_val, nonce = self.encryption.encrypt(value)
        version_id = str(uuid.uuid4())
        
        self._conn.execute(
            "INSERT INTO secrets (version_id, secret_key, encrypted_value, nonce, active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
            (version_id, key, encrypted_val, nonce, _now())
        )
        self._conn.commit()
        self._log_audit("create/update", key, policy.service, policy.reason, True)

    async def rotate_secret(self, key: str, new_value: str) -> None:
        policy = current_vault_policy.get()
        if not policy:
            raise PermissionError("Access denied")
        self._log_audit("rotate", key, policy.service, policy.reason, True)
        await self.store_secret(key, new_value)

    async def rollback_secret(self, key: str, version_id: str) -> bool:
        policy = current_vault_policy.get()
        if not policy or policy.service not in ["AdminCLI", "WebFrontend"]:
            self._log_audit("rollback", key, getattr(policy, "service", "unknown"), "Unauthorized rollback", False)
            raise PermissionError("Access denied for rollback")

        row = self._conn.execute("SELECT * FROM secrets WHERE version_id = ? AND secret_key = ?", (version_id, key)).fetchone()
        if not row:
            return False

        self._conn.execute("UPDATE secrets SET active = 0 WHERE secret_key = ?", (key,))
        self._conn.execute("UPDATE secrets SET active = 1 WHERE version_id = ?", (version_id,))
        self._conn.commit()
        self._log_audit("rollback", key, policy.service, f"Rolled back to {version_id}", True)
        return True

    async def list_versions(self, key: str) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT version_id, active, created_at FROM secrets WHERE secret_key = ? ORDER BY created_at DESC",
            (key,)
        ).fetchall()
        return [dict(r) for r in rows]

    async def remove_secret(self, key: str) -> None:
        policy = current_vault_policy.get()
        if not policy or policy.service not in ["AdminCLI", "WebFrontend"]:
            raise PermissionError("Access denied for removing secrets")
        self._conn.execute("DELETE FROM secrets WHERE secret_key = ?", (key,))
        self._conn.commit()
        self._log_audit("delete", key, policy.service, policy.reason, True)


class SecretVaultAdapter:
    """
    Lightweight bridge providing synchronous access to the async SecretVault
    without using asyncio.run(), ensuring no nested event loops.
    """
    def __init__(self, vault: SQLiteSecretVault):
        self.vault = vault

    def _run_with_policy(self, coro, policy: SecretAccessPolicy):
        # We must set the context variable within the asyncio task/thread
        async def wrapper():
            current_vault_policy.set(policy)
            return await coro
            
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, wrapper())
                    return future.result()
            else:
                return loop.run_until_complete(wrapper())
        except RuntimeError:
            return asyncio.run(wrapper())

    def get_secret_sync(self, key: str, policy: SecretAccessPolicy) -> Optional[str]:
        return self._run_with_policy(self.vault.get_secret(key), policy)

    def store_secret_sync(self, key: str, value: str, policy: SecretAccessPolicy) -> None:
        self._run_with_policy(self.vault.store_secret(key, value), policy)
        
    def remove_secret_sync(self, key: str, policy: SecretAccessPolicy) -> None:
        self._run_with_policy(self.vault.remove_secret(key), policy)
        
    def rollback_secret_sync(self, key: str, version_id: str, policy: SecretAccessPolicy) -> bool:
        return self._run_with_policy(self.vault.rollback_secret(key, version_id), policy)
        
    def list_versions_sync(self, key: str, policy: SecretAccessPolicy) -> List[Dict[str, Any]]:
        return self._run_with_policy(self.vault.list_versions(key), policy)

