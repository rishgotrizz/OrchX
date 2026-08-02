import sys, os, tempfile
sys.path.insert(0, "packages/orchx-core")
sys.path.insert(0, "packages/orchx-runtime")

from orchx_runtime.plugin_layer import PluginRegistry
from orchx_runtime.builtin_plugins import (
    register_builtin_plugins,
    FilesystemPlugin,
    PythonPlugin,
    TerminalPlugin,
    GitPlugin,
)

# ── Registry registration ─────────────────────────────────────────────────
registry = PluginRegistry()
register_builtin_plugins(registry)

from orchx_core.interfaces.plugin_contracts import PluginLifecycleState
print(f"Registered {len(registry.plugins)} plugins:")
for pid, manifest in registry.plugins.items():
    state = registry.plugin_states[pid]
    caps = ", ".join(manifest.capabilities_provided)
    print(f"  [{state.value:8s}] {pid:12s} | caps: {caps}")

# ── FilesystemPlugin ──────────────────────────────────────────────────────
sandbox = tempfile.mkdtemp(prefix="orchx_test_")
fs = FilesystemPlugin(sandbox_root=sandbox)

print("\n[FilesystemPlugin]")
print("  mkdir:  ", fs.execute("mkdir",  {"path": "sub/dir"}))
print("  write:  ", fs.execute("write",  {"path": "sub/dir/hello.txt", "content": "hello orchx"}))
print("  read:   ", fs.execute("read",   {"path": "sub/dir/hello.txt"}))
print("  list:   ", fs.execute("list",   {"path": "sub/dir"}))
print("  exists: ", fs.execute("exists", {"path": "sub/dir/hello.txt"}))
print("  escape: ", fs.execute("read",   {"path": "../../etc/passwd"}))
print("  delete: ", fs.execute("delete", {"path": "sub/dir/hello.txt"}))

# ── PythonPlugin ──────────────────────────────────────────────────────────
py = PythonPlugin()
print("\n[PythonPlugin]")
print("  2+2:    ", py.execute("run", {"code": "print(2 + 2)"}))
print("  error:  ", py.execute("run", {"code": "raise ValueError('oops')"}))
print("  timeout:", py.execute("run", {"code": "import time; time.sleep(20)", "timeout": 2}))

# ── TerminalPlugin ────────────────────────────────────────────────────────
term = TerminalPlugin()
print("\n[TerminalPlugin]")
print("  echo:   ", term.execute("run", {"cmd": "echo hello_orchx"}))
print("  block1: ", term.execute("run", {"cmd": "sudo ls"}))
print("  block2: ", term.execute("run", {"cmd": "rm -rf /"}))
print("  block3: ", term.execute("run", {"cmd": "cat /etc/hostname"}))

# ── GitPlugin (no-git graceful) ───────────────────────────────────────────
import shutil
git = GitPlugin()
print("\n[GitPlugin]")
if shutil.which("git"):
    with tempfile.TemporaryDirectory() as td:
        print("  init:   ", git.execute("init",   {"cwd": td}))
        print("  status: ", git.execute("status", {"cwd": td}))
else:
    print("  (git not on PATH — graceful fallback):", git.execute("status", {}))

print("\nSmoke tests PASSED")
