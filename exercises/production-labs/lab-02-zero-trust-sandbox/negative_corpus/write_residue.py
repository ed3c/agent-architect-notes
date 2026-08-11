from pathlib import Path


Path("/tmp/agent-residue").write_text("ephemeral")
print("RESIDUE_WRITTEN")
