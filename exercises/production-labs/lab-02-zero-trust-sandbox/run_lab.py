"""Execute the negative corpus and print a machine-readable local receipt."""

import json
import os

from sandbox_runner import DockerSandbox, SandboxPolicy


def main() -> int:
    sandbox = DockerSandbox(SandboxPolicy())
    receipt = {}

    scenarios = [
        ("success_cleanup", "success.py", 0, False),
        ("filesystem", "forbidden_filesystem.py", 0, False),
        ("network", "outbound_network.py", 0, False),
        ("credential_isolation", "credential_isolation.py", 0, False),
        ("memory", "memory_exhaustion.py", None, False),
        ("process", "process_exhaustion.py", 0, False),
        ("failure_cleanup", "explicit_failure.py", 7, False),
        ("timeout_cleanup", "infinite_loop.py", 124, True),
        ("residue_write", "write_residue.py", 0, False),
        ("residue_check", "check_residue.py", 0, False),
    ]

    original_canary = os.environ.get("PRODUCTION_SECRET")
    os.environ["PRODUCTION_SECRET"] = "mock-host-canary"
    try:
        for name, script, expected_code, expected_timeout in scenarios:
            timeout = 1 if expected_timeout else 8
            result = sandbox.run_script(script, timeout_seconds=timeout)
            expected_exit = (
                result.returncode != 0
                if expected_code is None
                else result.returncode == expected_code
            )
            cleaned = not sandbox.container_exists(result.container_name)
            receipt[name] = {
                "cleaned": cleaned,
                "passed": expected_exit
                and result.timed_out == expected_timeout
                and cleaned,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "timed_out": result.timed_out,
            }
    finally:
        if original_canary is None:
            os.environ.pop("PRODUCTION_SECRET", None)
        else:
            os.environ["PRODUCTION_SECRET"] = original_canary

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all(item["passed"] for item in receipt.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
