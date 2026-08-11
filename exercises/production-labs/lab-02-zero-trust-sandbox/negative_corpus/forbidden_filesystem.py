from pathlib import Path


try:
    Path("/etc/shadow").read_text()
except PermissionError:
    pass
else:
    raise AssertionError("non-root sandbox unexpectedly read /etc/shadow")

try:
    Path("/etc/agent-residue").write_text("must not persist")
except OSError:
    pass
else:
    raise AssertionError("read-only root filesystem accepted a write")

if Path("/host-secret").exists():
    raise AssertionError("unmounted host path became visible")

print("FILESYSTEM_BLOCKED")
