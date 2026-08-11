import unittest

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


if __name__ == "__main__":
    unittest.main()
