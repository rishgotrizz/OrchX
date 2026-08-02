#!/usr/bin/env python3
import sys
import argparse
import getpass
import json
import asyncio
from typing import Dict
from orchx_runtime.infrastructure_layer import ProviderCredentialManager
from orchx_runtime.vault import SecretAccessPolicy

def get_manager() -> ProviderCredentialManager:
    return ProviderCredentialManager()

def cmd_add(args):
    manager = get_manager()
    meta = manager.metadata_registry.get(args.provider)
    if not meta:
        print(f"Error: Unsupported provider '{args.provider}'")
        sys.exit(1)
        
    creds = {}
    print(f"Adding credentials for {meta.display_name}")
    for req in meta.required_credentials:
        val = getpass.getpass(prompt=f"{req} (required): ")
        if not val.strip():
            print("Error: Required credential cannot be empty.")
            sys.exit(1)
        creds[req] = val.strip()
        
    for opt in meta.optional_credentials:
        val = getpass.getpass(prompt=f"{opt} (optional): ")
        if val.strip():
            creds[opt] = val.strip()
            
    errors = manager.validate_and_store(args.provider, creds)
    if errors:
        print(f"Validation failed: {errors}")
        sys.exit(1)
    print(f"Successfully added credentials for {args.provider}.")

def cmd_list(args):
    manager = get_manager()
    providers = manager.metadata_registry.list_all()
    print(f"{'Provider ID':<20} | {'Display Name':<20} | {'Status'}")
    print("-" * 60)
    for p in providers:
        # Check if we have credentials
        policy = SecretAccessPolicy(
            service="AdminCLI",
            provider=p.provider_id,
            reason="CLI List",
            request_id="cli-list"
        )
        try:
            sec = manager.vault_adapter.get_secret_sync(f"{p.provider_id}_api_key", policy)
            status = "Configured" if sec else "Not Configured"
        except Exception:
            status = "Not Configured"
        print(f"{p.provider_id:<20} | {p.display_name:<20} | {status}")

def cmd_validate(args):
    manager = get_manager()
    policy = SecretAccessPolicy(
        service="AdminCLI",
        provider=args.provider,
        reason="CLI Validate",
        request_id="cli-validate"
    )
    sec = manager.vault_adapter.get_secret_sync(f"{args.provider}_api_key", policy)
    if not sec:
        print(f"No credentials configured for {args.provider}")
        sys.exit(1)
    print(f"Credentials for {args.provider} are present and decrypt successfully.")

def cmd_rotate(args):
    print("Rotating credentials (will prompt for new values)")
    cmd_add(args)

def cmd_rollback(args):
    manager = get_manager()
    policy = SecretAccessPolicy(
        service="AdminCLI",
        provider=args.provider,
        reason="CLI Rollback",
        request_id="cli-rollback"
    )
    key = f"{args.provider}_api_key"
    
    versions = manager.vault_adapter.list_versions_sync(key, policy)
    if not versions:
        print("No versions found.")
        sys.exit(1)
        
    print(f"{'Version ID':<40} | {'Active':<8} | {'Created At'}")
    print("-" * 80)
    for v in versions:
        print(f"{v['version_id']:<40} | {str(bool(v['active'])):<8} | {v['created_at']}")
        
    vid = input("Enter Version ID to rollback to: ").strip()
    if not vid:
        sys.exit(0)
        
    success = manager.vault_adapter.rollback_secret_sync(key, vid, policy)
    if success:
        print("Rollback successful.")
    else:
        print("Rollback failed.")

def cmd_remove(args):
    manager = get_manager()
    policy = SecretAccessPolicy(
        service="AdminCLI",
        provider=args.provider,
        reason="CLI Remove",
        request_id="cli-remove"
    )
    key = f"{args.provider}_api_key"
    
    manager.vault_adapter.remove_secret_sync(key, policy)
    print(f"Credentials removed for {args.provider}")

def cmd_health(args):
    manager = get_manager()
    try:
        caps = manager.get_capabilities(args.provider)
        print(f"Health Check Passed for {args.provider}.")
        print(f"Live Discovery: {caps.live_discovery}")
        print(f"Models: {caps.models}")
    except Exception as e:
        print(f"Health Check failed for {args.provider}: {e}")

def main():
    parser = argparse.ArgumentParser(description="OrchX Secret Vault CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add
    p_add = subparsers.add_parser("add", help="Add provider credentials")
    p_add.add_argument("provider", help="Provider ID (e.g. openai, anthropic)")
    
    # List
    p_list = subparsers.add_parser("list", help="List all providers and their status")
    
    # Validate
    p_validate = subparsers.add_parser("validate", help="Validate stored credentials")
    p_validate.add_argument("provider", help="Provider ID")
    
    # Rotate
    p_rotate = subparsers.add_parser("rotate", help="Rotate provider credentials")
    p_rotate.add_argument("provider", help="Provider ID")
    
    # Rollback
    p_rollback = subparsers.add_parser("rollback", help="Rollback to previous credential version")
    p_rollback.add_argument("provider", help="Provider ID")
    
    # Remove
    p_remove = subparsers.add_parser("remove", help="Remove provider credentials")
    p_remove.add_argument("provider", help="Provider ID")
    
    # Health
    p_health = subparsers.add_parser("health", help="Check provider health/capabilities")
    p_health.add_argument("provider", help="Provider ID")
    
    args = parser.parse_args()
    
    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "validate": cmd_validate,
        "rotate": cmd_rotate,
        "rollback": cmd_rollback,
        "remove": cmd_remove,
        "health": cmd_health
    }
    
    commands[args.command](args)

if __name__ == "__main__":
    main()
