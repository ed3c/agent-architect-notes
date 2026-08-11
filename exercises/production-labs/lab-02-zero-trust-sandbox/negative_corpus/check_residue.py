from pathlib import Path


if Path("/tmp/agent-residue").exists():
    raise AssertionError("tmpfs residue survived container cleanup")

print("RESIDUE_ABSENT")
