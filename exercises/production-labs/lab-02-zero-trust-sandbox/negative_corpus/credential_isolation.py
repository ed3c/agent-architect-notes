import os
from pathlib import Path


if os.environ.get("PRODUCTION_SECRET") is not None:
    raise AssertionError("host environment credential was injected")

if Path("/run/secrets/production").exists():
    raise AssertionError("production credential path was mounted")

print("CREDENTIAL_ABSENT")
