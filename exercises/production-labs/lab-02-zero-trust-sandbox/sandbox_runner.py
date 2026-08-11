"""Default-deny Docker runner for the zero-trust sandbox learning lab."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import uuid


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


@dataclass(frozen=True)
class SandboxResult:
    container_name: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


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

    def run_script(self, script_name: str, *, timeout_seconds: float) -> SandboxResult:
        script_path = self._corpus_dir / script_name
        if not script_path.is_file():
            raise FileNotFoundError(f"negative corpus script not found: {script_name}")

        container_name = f"agent-sandbox-{uuid.uuid4().hex[:12]}"
        command = self.build_command(script_name, container_name)

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            return SandboxResult(
                container_name=container_name,
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as error:
            return SandboxResult(
                container_name=container_name,
                returncode=124,
                stdout=_timeout_text(error.stdout),
                stderr=_timeout_text(error.stderr),
                timed_out=True,
            )
        finally:
            self._remove_container(container_name)

    def container_exists(self, container_name: str) -> bool:
        completed = subprocess.run(
            ["docker", "container", "inspect", container_name],
            capture_output=True,
            text=True,
            check=False,
        )
        return completed.returncode == 0

    def _remove_container(self, container_name: str) -> None:
        subprocess.run(
            ["docker", "container", "rm", "--force", container_name],
            capture_output=True,
            text=True,
            check=False,
        )


def _timeout_text(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
