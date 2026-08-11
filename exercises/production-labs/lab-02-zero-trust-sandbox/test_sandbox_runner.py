import unittest
from unittest.mock import patch

from sandbox_runner import DockerSandbox, SandboxPolicy


class SandboxCommandContractTests(unittest.TestCase):
    def test_default_policy_compiles_to_default_deny_docker_flags(self):
        sandbox = DockerSandbox(SandboxPolicy())

        command = sandbox.build_command("success.py", "sandbox-contract-test")

        self.assertEqual(command[:3], ["docker", "run", "--rm"])
        self.assertInSequence(command, "--network", "none")
        self.assertIn("--read-only", command)
        self.assertInSequence(command, "--cap-drop", "ALL")
        self.assertInSequence(command, "--security-opt", "no-new-privileges")
        self.assertInSequence(command, "--pids-limit", "32")
        self.assertInSequence(command, "--memory", "64m")
        self.assertInSequence(command, "--cpus", "0.50")
        self.assertInSequence(command, "--user", "65534:65534")
        self.assertInSequence(command, "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m")
        self.assertNotIn("PRODUCTION_SECRET", " ".join(command))

    def assertInSequence(self, values, first, second):
        index = values.index(first)
        self.assertEqual(values[index + 1], second)


class SandboxExecutionContractTests(unittest.TestCase):
    def test_successful_run_is_removed_after_exit(self):
        sandbox = DockerSandbox(SandboxPolicy())

        result = sandbox.run_script("success.py", timeout_seconds=5)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "SANDBOX_OK")
        self.assertFalse(result.timed_out)
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_forbidden_host_and_root_filesystem_access_is_blocked(self):
        sandbox = DockerSandbox(SandboxPolicy())

        result = sandbox.run_script("forbidden_filesystem.py", timeout_seconds=5)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "FILESYSTEM_BLOCKED")
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_outbound_network_access_is_blocked(self):
        sandbox = DockerSandbox(SandboxPolicy())

        result = sandbox.run_script("outbound_network.py", timeout_seconds=5)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "NETWORK_BLOCKED")
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_host_credential_canary_is_not_injected_into_sandbox(self):
        sandbox = DockerSandbox(SandboxPolicy())

        with patch.dict("os.environ", {"PRODUCTION_SECRET": "mock-host-canary"}):
            result = sandbox.run_script(
                "credential_isolation.py", timeout_seconds=5
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "CREDENTIAL_ABSENT")
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_timeout_forces_cleanup(self):
        sandbox = DockerSandbox(SandboxPolicy())

        result = sandbox.run_script("infinite_loop.py", timeout_seconds=1)

        self.assertEqual(result.returncode, 124)
        self.assertTrue(result.timed_out)
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_nonzero_exit_still_cleans_up(self):
        sandbox = DockerSandbox(SandboxPolicy())

        result = sandbox.run_script("explicit_failure.py", timeout_seconds=5)

        self.assertEqual(result.returncode, 7)
        self.assertFalse(result.timed_out)
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_memory_exhaustion_is_stopped_by_container_limit(self):
        sandbox = DockerSandbox(SandboxPolicy())

        result = sandbox.run_script("memory_exhaustion.py", timeout_seconds=5)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_process_exhaustion_hits_pid_limit(self):
        sandbox = DockerSandbox(SandboxPolicy())

        result = sandbox.run_script("process_exhaustion.py", timeout_seconds=8)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PIDS_BLOCKED")
        self.assertFalse(sandbox.container_exists(result.container_name))

    def test_tmpfs_residue_does_not_survive_cleanup(self):
        sandbox = DockerSandbox(SandboxPolicy())

        writer = sandbox.run_script("write_residue.py", timeout_seconds=5)
        reader = sandbox.run_script("check_residue.py", timeout_seconds=5)

        self.assertEqual(writer.returncode, 0, writer.stderr)
        self.assertEqual(reader.returncode, 0, reader.stderr)
        self.assertEqual(reader.stdout.strip(), "RESIDUE_ABSENT")
        self.assertFalse(sandbox.container_exists(writer.container_name))
        self.assertFalse(sandbox.container_exists(reader.container_name))


if __name__ == "__main__":
    unittest.main()
