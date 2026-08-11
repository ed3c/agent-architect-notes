# LAB-AA-02：Zero-trust Agent Code Sandbox

> Issue: [#3](https://github.com/ed3c/agent-architect-notes/issues/3)
> Evidence stage: `executed-local`
> Boundary: Docker Engine / runc on OrbStack；untrusted Python corpus

## Objective

把 Agent-generated code 當 untrusted input，在不放入 production credential、不停用 host protection 的情況下，驗證 default-deny container profile 是否能阻擋指定 attack corpus，並在 success、failure、timeout 後清除 execution state。

這是 Docker/runc learning Lab，不是 generic secure-code-execution product，也不是 kernel exploit resistance 證明。

## Tested Platform

- Host: macOS `26.4.0` / arm64；OrbStack Docker context
- Docker Client: `29.4.0`
- Docker Engine: `29.4.0`；Linux kernel `7.0.14-orbstack-00380-ga7e0a2dc9535`
- containerd `v2.2.2`；runc `1.5.1`
- Image: `python@sha256:94c50be2dc994b873b55bc123e95e6dbade08095b3dfd790f51c34de3f08cbb7`

Image 必須已存在於 local daemon；runner 不做 pull，qualification receipt 應確認實際 digest。

## Trust Boundary

| Zone | Trust | Capability |
| --- | --- | --- |
| Host orchestrator / `sandbox_runner.py` | trusted control plane | compile policy、start/kill/remove container、收集 bounded stdout/stderr |
| `negative_corpus/*.py` | untrusted workload | 只在 `/work` read-only mount 內被 Python 讀取；不能取得 Docker socket |
| Container | hostile execution zone | non-root、no external network、read-only rootfs、ephemeral `/tmp`、bounded resources |
| External services / production secrets | unavailable | 沒有 route、credential mount 或 host environment passthrough |

Approval point：任何新增 mount、network、capability、device、credential 或 writable persistent volume 都是 policy expansion，必須另開 review，不能由 workload 自己要求。

## Default-deny Profile

| Control | Docker flag | Local assertion |
| --- | --- | --- |
| Network | `--network none` | outbound TCP to public IP raises `OSError` |
| Root filesystem | `--read-only` | write under `/etc` blocked |
| Host filesystem | only corpus bind-mounted read-only | unmounted `/host-secret` absent；`/etc/shadow` unreadable as non-root |
| Identity | `--user 65534:65534` | forbidden root-owned file read blocked |
| Linux capabilities | `--cap-drop ALL` | command contract asserted；沒有逐 capability exploit test |
| Privilege escalation | `--security-opt no-new-privileges` | command contract asserted |
| Processes | `--pids-limit 32` | 100-child attempt reaches `OSError` / `PIDS_BLOCKED` |
| Memory | `--memory 64m` | 256 MiB allocation exits `137` |
| CPU | `--cpus 0.50` | command contract asserted；沒有精準 CPU scheduler benchmark |
| Wall time | host `subprocess.run(..., timeout=1)` | infinite loop returns synthetic `124` and container is removed |
| Writable state | `--tmpfs /tmp:rw,noexec,nosuid,size=16m` | marker exists in first run、next run reports `RESIDUE_ABSENT` |
| Environment | only explicit `HOME` / `PATH` passed | mock host `PRODUCTION_SECRET` canary is absent inside container |
| Image provenance | immutable digest | mutable tag 不進 execution command |

Docker daemon 的 default seccomp/AppArmor/SELinux 狀態未在本 Lab 獨立量測，不能把它們列為已驗證 control。

## Run

Prerequisite：Docker daemon 可用，pinned image 已存在。

```bash
python3 -m unittest discover \
  -s exercises/production-labs/lab-02-zero-trust-sandbox \
  -p 'test_*.py' -v
```

Expected：`10 tests`、exit code `0`。

Machine-readable receipt：

```bash
python3 exercises/production-labs/lab-02-zero-trust-sandbox/run_lab.py
```

Expected：10 scenarios 的 `passed` / `cleaned` 都是 `true`；process exit code `0`。

Cleanup inventory check：

```bash
docker ps -a --filter name=agent-sandbox \
  --format '{{.ID}} {{.Names}} {{.Status}}'
```

Expected：empty output。

## Negative Corpus

| Script | Threat / assertion |
| --- | --- |
| `forbidden_filesystem.py` | host path discovery、root-owned read、rootfs write |
| `outbound_network.py` | direct-IP exfiltration attempt |
| `credential_isolation.py` | host env canary / production credential path discovery |
| `memory_exhaustion.py` | memory DoS |
| `process_exhaustion.py` | process-table DoS |
| `infinite_loop.py` | CPU/time exhaustion + timeout cleanup |
| `explicit_failure.py` | nonzero failure cleanup |
| `write_residue.py` + `check_residue.py` | residual state after cleanup |
| `success.py` | success-path cleanup |

## Credential and Confused-deputy Contract

本 Lab 完全不提供 credential：mock host canary 只用來證明沒有 environment passthrough。Production Tool use 必須由 sandbox 外的 broker 依 run/user/tool/action 做 authorization，回傳最小結果或短效 capability；raw long-lived secret 不得進 sandbox。Broker 尚未實作，因此 credentialed Tool execution evidence 是 `unknown`。

Prompt injection 只能產生 untrusted workload text，不能修改 `SandboxPolicy`。若 Agent 要求 `--network host`、Docker socket、host home mount、privileged mode 或 real credential，orchestrator 必須拒絕或送 human approval，而不是把自然語言當 authority。

## Known Limits

- Docker container 與 host VM 共享 Linux kernel；本 Lab 不抵抗未知 kernel / runc escape。
- `network=none` 不等於 application-layer allowlist；若 production 開放 egress，仍需 proxy/DNS/IP/rebinding 與 identity policy。
- 沒測 symlink race、Unix socket、device、GPU、shared-memory、side channel、fork bomb beyond PID limit 或 output-volume exhaustion。
- stdout/stderr 尚未做 byte cap / redaction；production 必須加上。
- Cleanup evidence 是 container inventory 與 tmpfs non-persistence；不證明 storage driver 已 forensic erase data。
- 只有 local arm64 OrbStack evidence；gVisor、Kubernetes、Firecracker/MicroVM 保持 `unknown`。

## Evidence and Review

- Threat model / sources：[Zero-trust Agent Sandbox](../../../docs/kb/zero-trust-agent-sandbox.md)
- System Design：[SD-AA-02](../../system-design/sd-02-zero-trust-agent-code-sandbox.md)
- Security receipt：[2026-08-11 report](../../../docs/eval-reports/2026-08-11-zero-trust-sandbox.md)
- What-if：workload 要求 network egress 下載 dependency，同時 Tool broker 可讀 customer data；請指出 capability split、approval、audit 與 cleanup path。
- Next review：`2026-08-12` 做第一次 active recall；`2026-08-18` 重跑 What-if 與至少一個新 negative case。
