"""Default-deny Docker runner for the zero-trust sandbox learning lab."""

from dataclasses import dataclass
from pathlib import Path


PYTHON_IMAGE = (
    "python@sha256:94c50be2dc994b873b55bc123e95e6dbade08095b3dfd790f51c34de3f08cbb7"
)


@dataclass(frozen=True)
class SandboxPolicy:
    cpu_limit: str = "0.50"
    memory_limit: str = "64m"
    pids_limit: int = 32
    tmpfs_size: str = "16m"
    user: str = "65534:65534"


class DockerSandbox:
    def __init__(self, policy: SandboxPolicy) -> None:
        self._policy = policy
        self._corpus_dir = Path(__file__).with_name("negative_corpus").resolve()

    def build_command(self, script_name: str, container_name: str) -> list[str]:
        if Path(script_name).name != script_name or not script_name.endswith(".py"):
            raise ValueError("script_name must be one Python file in negative_corpus")

        policy = self._policy
        return [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(policy.pids_limit),
            "--memory",
            policy.memory_limit,
            "--cpus",
            policy.cpu_limit,
            "--user",
            policy.user,
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,size={policy.tmpfs_size}",
            "--env",
            "HOME=/tmp",
            "--env",
            "PATH=/usr/local/bin:/usr/bin:/bin",
            "--mount",
            f"type=bind,src={self._corpus_dir},dst=/work,readonly",
            "--workdir",
            "/work",
            PYTHON_IMAGE,
            "python",
            f"/work/{script_name}",
        ]
