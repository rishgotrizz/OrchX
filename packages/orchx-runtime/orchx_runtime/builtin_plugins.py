"""
builtin_plugins.py
==================
Real, subprocess-based plugin executor implementations for OrchX.

Each executor class exposes:
  - plugin_id            : str             (class attribute, unique registry key)
  - plugin_name          : str             (class attribute, human-readable label)
  - capabilities_provided: List[str]       (class attribute)
  - execute(command, args) -> dict         ({success: bool, output: str, error: str})

The module-level helper ``register_builtin_plugins(registry)`` creates a
``PluginManifest`` for every executor and registers it in the supplied
``PluginRegistry`` with state ``PluginLifecycleState.ENABLED``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

from orchx_core.interfaces.plugin_contracts import (
    PluginLifecycleState,
    PluginManifest,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ok(output: str) -> dict:
    """Return a standard success result dict."""
    return {"success": True, "output": output, "error": ""}


def _err(error: str, output: str = "") -> dict:
    """Return a standard failure result dict."""
    return {"success": False, "output": output, "error": error}


def _run(args: List[str], timeout: int = 30, **kwargs) -> dict:
    """
    Run *args* via subprocess.run and return a normalised result dict.

    Extra keyword arguments are forwarded to ``subprocess.run``.
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            **kwargs,
        )
        if result.returncode == 0:
            return _ok(result.stdout)
        return _err(result.stderr.strip(), result.stdout)
    except subprocess.TimeoutExpired:
        return _err(f"Command timed out after {timeout}s")
    except FileNotFoundError:
        return _err(f"Executable not found: {args[0]}")
    except Exception as exc:  # pragma: no cover
        return _err(str(exc))


# ---------------------------------------------------------------------------
# 1. GitPlugin
# ---------------------------------------------------------------------------

class GitPlugin:
    """Executes real ``git`` CLI commands via subprocess."""

    plugin_id: str = "git"
    plugin_name: str = "Git Version Control"
    capabilities_provided: List[str] = ["git", "version_control"]

    # Commands that map directly to ``git <command>`` with optional extra flags.
    _SUPPORTED: Dict[str, List[str]] = {
        "status":  ["status", "--short"],
        "log":     ["log", "--oneline", "-20"],
        "diff":    ["diff"],
        "clone":   ["clone"],
        "commit":  ["commit"],
        "push":    ["push"],
        "pull":    ["pull"],
        "init":    ["init"],
    }

    def execute(self, command: str, args: dict) -> dict:
        """
        Run a git sub-command.

        ``args`` may contain:
          - ``cwd``    : working directory (str)  [optional, defaults to CWD]
          - ``flags``  : extra CLI flags (List[str]) [optional]
          - ``target`` : positional argument, e.g. clone URL or commit message
        """
        if not shutil.which("git"):
            return _err("git is not installed or not on PATH")

        if command not in self._SUPPORTED:
            return _err(
                f"Unsupported git command '{command}'. "
                f"Supported: {sorted(self._SUPPORTED)}"
            )

        git_args = ["git"] + self._SUPPORTED[command]

        # Append target (e.g. repo URL for clone, message fragment for commit)
        target = args.get("target")
        if target:
            git_args.append(str(target))

        # Append any extra caller-supplied flags
        for flag in args.get("flags", []):
            git_args.append(str(flag))

        cwd = args.get("cwd") or None
        return _run(git_args, timeout=60, cwd=cwd)


# ---------------------------------------------------------------------------
# 2. FilesystemPlugin
# ---------------------------------------------------------------------------

class FilesystemPlugin:
    """
    Safe filesystem operations confined to a configurable sandbox root.

    All paths are resolved and validated to be inside ``sandbox_root``
    before any operation is performed.  Attempts to escape via ``..``
    or symlinks that point outside the sandbox are rejected.
    """

    plugin_id: str = "filesystem"
    plugin_name: str = "Filesystem Operations"
    capabilities_provided: List[str] = ["filesystem", "file_read", "file_write"]

    DEFAULT_SANDBOX: Path = Path("/tmp/orchx_sandbox")

    def __init__(self, sandbox_root: str | os.PathLike | None = None) -> None:
        self.sandbox_root: Path = (
            Path(sandbox_root).resolve() if sandbox_root else self.DEFAULT_SANDBOX.resolve()
        )
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _safe_path(self, rel: str) -> Path | None:
        """
        Resolve *rel* relative to ``sandbox_root``.

        Returns ``None`` if the resolved path escapes the sandbox.
        """
        try:
            candidate = (self.sandbox_root / rel).resolve()
        except Exception:
            return None
        # Ensure the resolved path is still inside sandbox_root
        try:
            candidate.relative_to(self.sandbox_root)
        except ValueError:
            return None
        return candidate

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def execute(self, command: str, args: dict) -> dict:
        """
        Perform a filesystem operation.

        Required ``args`` keys vary by command:
          - ``read``   : path (str)
          - ``write``  : path (str), content (str)
          - ``list``   : path (str, defaults to sandbox root)
          - ``exists`` : path (str)
          - ``delete`` : path (str)
          - ``mkdir``  : path (str)
        """
        dispatch = {
            "read":   self._read,
            "write":  self._write,
            "list":   self._list,
            "exists": self._exists,
            "delete": self._delete,
            "mkdir":  self._mkdir,
        }
        handler = dispatch.get(command)
        if handler is None:
            return _err(
                f"Unsupported command '{command}'. Supported: {sorted(dispatch)}"
            )
        return handler(args)

    def _resolve(self, args: dict, key: str = "path") -> tuple:
        """Resolve and validate *args[key]*; return (path, error_dict_or_None)."""
        raw = args.get(key, "")
        path = self._safe_path(str(raw))
        if path is None:
            return None, _err(
                f"Path '{raw}' is outside sandbox '{self.sandbox_root}' or is invalid."
            )
        return path, None

    def _read(self, args: dict) -> dict:
        path, err = self._resolve(args)
        if err:
            return err
        if not path.is_file():
            return _err(f"File not found: {path}")
        try:
            return _ok(path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            return _err(str(exc))

    def _write(self, args: dict) -> dict:
        path, err = self._resolve(args)
        if err:
            return err
        content = args.get("content", "")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(content), encoding="utf-8")
            return _ok(f"Written {len(content)} chars to {path}")
        except OSError as exc:
            return _err(str(exc))

    def _list(self, args: dict) -> dict:
        raw = args.get("path", "")
        path = self._safe_path(str(raw)) if raw else self.sandbox_root
        if path is None:
            return _err(f"Path '{raw}' is outside sandbox.")
        if not path.exists():
            return _err(f"Directory not found: {path}")
        try:
            entries = sorted(p.name + ("/" if p.is_dir() else "") for p in path.iterdir())
            return _ok("\n".join(entries))
        except OSError as exc:
            return _err(str(exc))

    def _exists(self, args: dict) -> dict:
        path, err = self._resolve(args)
        if err:
            return err
        return _ok(str(path.exists()))

    def _delete(self, args: dict) -> dict:
        path, err = self._resolve(args)
        if err:
            return err
        if not path.exists():
            return _err(f"Path does not exist: {path}")
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            return _ok(f"Deleted: {path}")
        except OSError as exc:
            return _err(str(exc))

    def _mkdir(self, args: dict) -> dict:
        path, err = self._resolve(args)
        if err:
            return err
        try:
            path.mkdir(parents=True, exist_ok=True)
            return _ok(f"Directory created: {path}")
        except OSError as exc:
            return _err(str(exc))


# ---------------------------------------------------------------------------
# 3. TerminalPlugin
# ---------------------------------------------------------------------------

class TerminalPlugin:
    """
    Executes arbitrary shell commands via ``subprocess.run(shell=True)``.

    Dangerous patterns are blocked before any subprocess is spawned.
    """

    plugin_id: str = "terminal"
    plugin_name: str = "Terminal / Shell"
    capabilities_provided: List[str] = ["terminal", "shell"]

    # Patterns that are always rejected (simple substring checks)
    _BLOCKED_PATTERNS: List[str] = [
        "rm -rf /",
        "rm -rf ~/",
        "sudo",
        "/etc/",
        "/sys/",
        "/proc/",
        "> /dev/",
        "mkfs",
        "dd if=",
        ":(){:|:&};:",    # fork bomb
    ]

    def _is_dangerous(self, cmd: str) -> str | None:
        """Return the matched pattern if *cmd* is dangerous, else None."""
        lower = cmd.lower()
        for pattern in self._BLOCKED_PATTERNS:
            if pattern.lower() in lower:
                return pattern
        return None

    def execute(self, command: str, args: dict) -> dict:
        """
        Run a shell command.

        ``args``:
          - ``cmd``    : the shell command string (str, required)
          - ``cwd``    : working directory (str, optional)
          - ``env``    : extra environment variables (dict, optional)
          - ``timeout``: override timeout in seconds (int, optional, max 120)

        Returns ``{success, output, error}`` with returncode embedded in output.
        """
        cmd_str = args.get("cmd", "")
        if not cmd_str:
            return _err("'cmd' argument is required")

        matched = self._is_dangerous(cmd_str)
        if matched:
            return _err(f"Command blocked — matches dangerous pattern: '{matched}'")

        cwd = args.get("cwd") or None
        timeout = min(int(args.get("timeout", 30)), 120)

        env = os.environ.copy()
        extra_env = args.get("env") or {}
        env.update({str(k): str(v) for k, v in extra_env.items()})

        try:
            result = subprocess.run(
                cmd_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env,
            )
            combined_output = (
                f"[returncode={result.returncode}]\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
            if result.returncode == 0:
                return _ok(combined_output)
            return _err(result.stderr.strip(), combined_output)
        except subprocess.TimeoutExpired:
            return _err(f"Shell command timed out after {timeout}s")
        except Exception as exc:  # pragma: no cover
            return _err(str(exc))


# ---------------------------------------------------------------------------
# 4. PythonPlugin
# ---------------------------------------------------------------------------

class PythonPlugin:
    """Executes Python 3 code snippets via ``python3 -c``."""

    plugin_id: str = "python"
    plugin_name: str = "Python Code Executor"
    capabilities_provided: List[str] = ["python", "code_execution"]

    _TIMEOUT: int = 10

    def execute(self, command: str, args: dict) -> dict:
        """
        Run a Python code snippet.

        ``args``:
          - ``code``   : Python source to execute (str, required)
          - ``timeout``: override timeout in seconds (int, optional, max 30)

        The ``command`` parameter is ignored (always runs the code snippet).
        """
        code = args.get("code", "")
        if not code:
            return _err("'code' argument is required")

        timeout = min(int(args.get("timeout", self._TIMEOUT)), 30)

        python_exe = shutil.which("python3") or shutil.which("python")
        if not python_exe:
            return _err("python3 is not installed or not on PATH")

        return _run([python_exe, "-c", code], timeout=timeout)


# ---------------------------------------------------------------------------
# 5. NodePlugin
# ---------------------------------------------------------------------------

class NodePlugin:
    """Executes JavaScript code snippets via ``node -e``."""

    plugin_id: str = "node"
    plugin_name: str = "Node.js JavaScript Executor"
    capabilities_provided: List[str] = ["node", "javascript"]

    _TIMEOUT: int = 30

    def execute(self, command: str, args: dict) -> dict:
        """
        Run a JavaScript code snippet.

        ``args``:
          - ``code``   : JavaScript source to evaluate (str, required)
          - ``timeout``: override timeout in seconds (int, optional, max 60)
        """
        if not shutil.which("node"):
            return _err("node is not installed or not on PATH")

        code = args.get("code", "")
        if not code:
            return _err("'code' argument is required")

        timeout = min(int(args.get("timeout", self._TIMEOUT)), 60)
        return _run(["node", "-e", code], timeout=timeout)


# ---------------------------------------------------------------------------
# 6. DockerPlugin
# ---------------------------------------------------------------------------

class DockerPlugin:
    """Wraps the ``docker`` CLI for container management."""

    plugin_id: str = "docker"
    plugin_name: str = "Docker Container Manager"
    capabilities_provided: List[str] = ["docker", "containers"]

    _SUPPORTED: Dict[str, List[str]] = {
        "ps":     ["ps"],
        "images": ["images"],
        "run":    ["run"],
        "stop":   ["stop"],
        "build":  ["build"],
    }

    def execute(self, command: str, args: dict) -> dict:
        """
        Run a docker sub-command.

        ``args``:
          - ``flags``  : extra CLI flags / positional args (List[str], optional)
          - ``timeout``: override timeout in seconds (int, optional, max 300)
        """
        if not shutil.which("docker"):
            return _err("docker is not installed or not on PATH")

        if command not in self._SUPPORTED:
            return _err(
                f"Unsupported docker command '{command}'. "
                f"Supported: {sorted(self._SUPPORTED)}"
            )

        docker_args = ["docker"] + self._SUPPORTED[command]
        for flag in args.get("flags", []):
            docker_args.append(str(flag))

        timeout = min(int(args.get("timeout", 30)), 300)
        return _run(docker_args, timeout=timeout)


# ---------------------------------------------------------------------------
# 7. BrowserPlugin
# ---------------------------------------------------------------------------

class BrowserPlugin:
    """Fetches URLs using the stdlib ``urllib.request`` — no external deps."""

    plugin_id: str = "browser"
    plugin_name: str = "Browser HTTP Fetcher"
    capabilities_provided: List[str] = ["browser", "http_fetch"]

    _MAX_CHARS: int = 5_000
    _TIMEOUT: int = 15

    def execute(self, command: str, args: dict) -> dict:
        """
        Fetch a URL and return the response body (truncated to 5 000 chars).

        ``args``:
          - ``url``    : URL to fetch (str, required)
          - ``timeout``: request timeout in seconds (int, optional, max 60)
          - ``headers``: additional HTTP headers dict (optional)

        Supported commands: ``fetch``.
        """
        if command != "fetch":
            return _err(
                f"Unsupported command '{command}'. Supported: ['fetch']"
            )

        url = args.get("url", "")
        if not url:
            return _err("'url' argument is required")

        timeout = min(int(args.get("timeout", self._TIMEOUT)), 60)

        try:
            req = urllib.request.Request(url)
            extra_headers: dict = args.get("headers") or {}
            for header_name, header_val in extra_headers.items():
                req.add_header(str(header_name), str(header_val))

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                # Over-read then truncate to avoid partial multi-byte chars
                content_bytes: bytes = resp.read(self._MAX_CHARS * 4)
                try:
                    body = content_bytes.decode("utf-8", errors="replace")
                except Exception:
                    body = repr(content_bytes)
                body = body[: self._MAX_CHARS]
                return _ok(body)
        except urllib.error.HTTPError as exc:
            return _err(f"HTTP {exc.code}: {exc.reason}", "")
        except urllib.error.URLError as exc:
            return _err(f"URL error: {exc.reason}", "")
        except TimeoutError:
            return _err(f"Request timed out after {timeout}s")
        except Exception as exc:  # pragma: no cover
            return _err(str(exc))


# ---------------------------------------------------------------------------
# 8. PlaywrightPlugin
# ---------------------------------------------------------------------------

class PlaywrightPlugin:
    """
    Browser automation via the ``playwright`` Python package.

    Falls back gracefully with a clear error when playwright is not installed.
    """

    plugin_id: str = "playwright"
    plugin_name: str = "Playwright Browser Automation"
    capabilities_provided: List[str] = ["playwright", "browser_automation"]

    _TIMEOUT: int = 30_000  # ms — playwright's native timeout unit

    def execute(self, command: str, args: dict) -> dict:
        """
        Run a playwright automation command.

        ``args``:
          - ``url``        : target URL (str, required for both commands)
          - ``output_path``: where to save screenshot PNG (str, required for 'screenshot')
          - ``browser``    : 'chromium' | 'firefox' | 'webkit' (str, optional, default 'chromium')

        Supported commands:
          - ``navigate``   : visit URL and return page title + HTML snippet
          - ``screenshot`` : visit URL and save a screenshot to ``output_path``
        """
        try:
            from playwright.sync_api import sync_playwright  # type: ignore[import]
        except ImportError:
            return _err(
                "playwright not installed. "
                "Run: pip install playwright && playwright install"
            )

        if command not in ("navigate", "screenshot"):
            return _err(
                f"Unsupported command '{command}'. Supported: ['navigate', 'screenshot']"
            )

        url = args.get("url", "")
        if not url:
            return _err("'url' argument is required")

        browser_type = args.get("browser", "chromium")

        try:
            with sync_playwright() as pw:
                browser_launcher = getattr(pw, browser_type, None)
                if browser_launcher is None:
                    return _err(
                        f"Unknown browser '{browser_type}'. "
                        "Choose: chromium, firefox, webkit"
                    )
                browser = browser_launcher.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=self._TIMEOUT)

                if command == "navigate":
                    title = page.title()
                    html_snippet = page.content()[:2_000]
                    browser.close()
                    return _ok(f"Title: {title}\n\nHTML (first 2000 chars):\n{html_snippet}")

                # command == "screenshot"
                output_path = args.get("output_path", "/tmp/orchx_screenshot.png")
                page.screenshot(path=str(output_path), full_page=False)
                browser.close()
                return _ok(f"Screenshot saved to: {output_path}")

        except Exception as exc:
            return _err(f"Playwright error: {exc}")

        # Unreachable, but satisfies type checkers
        return _err("Unhandled state in PlaywrightPlugin.execute")


# ---------------------------------------------------------------------------
# Registry helper
# ---------------------------------------------------------------------------

#: All executor classes in canonical registration order.
ALL_PLUGIN_EXECUTORS: List[type] = [
    GitPlugin,
    FilesystemPlugin,
    TerminalPlugin,
    PythonPlugin,
    NodePlugin,
    DockerPlugin,
    BrowserPlugin,
    PlaywrightPlugin,
]

# Minimal version / author metadata used when building PluginManifest objects.
_PLUGIN_META: Dict[str, Dict[str, Any]] = {
    "git": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": (
            "Real git CLI integration — "
            "status, log, diff, clone, commit, push, pull, init."
        ),
        "permissions": ["shell_exec"],
        "security_profile": "restricted",
    },
    "filesystem": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": (
            "Sandboxed filesystem operations — "
            "read, write, list, exists, delete, mkdir."
        ),
        "permissions": ["file_read", "file_write"],
        "security_profile": "sandboxed",
    },
    "terminal": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": (
            "Executes shell commands via subprocess "
            "with dangerous-pattern blocking."
        ),
        "permissions": ["shell_exec"],
        "security_profile": "restricted",
    },
    "python": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": (
            "Runs Python 3 code snippets via python3 -c "
            "with a 10-second timeout."
        ),
        "permissions": ["code_exec"],
        "security_profile": "restricted",
    },
    "node": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": "Runs JavaScript snippets via node -e.",
        "permissions": ["code_exec"],
        "security_profile": "restricted",
    },
    "docker": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": "Docker CLI integration — ps, images, run, stop, build.",
        "permissions": ["shell_exec", "network"],
        "security_profile": "restricted",
    },
    "browser": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": (
            "Fetches HTTP/HTTPS URLs via urllib; "
            "returns truncated HTML body (5 000 chars max)."
        ),
        "permissions": ["network"],
        "security_profile": "standard",
    },
    "playwright": {
        "version": "1.0.0",
        "author": "OrchX Core Team",
        "description": (
            "Browser automation via playwright — "
            "navigate and screenshot commands."
        ),
        "permissions": ["network", "file_write"],
        "security_profile": "restricted",
    },
}


def register_builtin_plugins(registry: Any) -> None:  # noqa: ANN401
    """
    Create a ``PluginManifest`` for each built-in executor and register it in
    *registry* with state ``PluginLifecycleState.ENABLED``.

    Parameters
    ----------
    registry:
        An instance of ``orchx_runtime.plugin_layer.PluginRegistry``.
        Typed as ``Any`` to avoid a circular import; the structural interface
        (``register_plugin(manifest, state)``) is all that is required.
    """
    for executor_cls in ALL_PLUGIN_EXECUTORS:
        pid = executor_cls.plugin_id
        meta = _PLUGIN_META[pid]

        manifest = PluginManifest(
            plugin_id=pid,
            name=executor_cls.plugin_name,
            version=meta["version"],
            author=meta["author"],
            description=meta["description"],
            capabilities_provided=list(executor_cls.capabilities_provided),
            permissions_requested=meta["permissions"],
            supported_platforms=["linux", "darwin", "win32"],
            security_profile=meta["security_profile"],
        )

        registry.register_plugin(manifest, state=PluginLifecycleState.ENABLED)
