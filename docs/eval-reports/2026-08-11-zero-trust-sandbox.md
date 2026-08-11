# 2026-08-11 — Zero-trust Sandbox Security Evidence

> Exercise ID: `LAB-AA-02`
> Issue: [#3](https://github.com/ed3c/agent-architect-notes/issues/3)
> Evidence level: `LOCAL_OBSERVATION / executed-local`

## Scope

在 local OrbStack Docker Engine 上執行 pinned Python image 與 hostile negative corpus，記錄指定 filesystem、network、credential、resource、timeout 與 residual-state attempts 的 observable result。

此報告只說「tested environment 實際觀察到什麼」，不把 container test 外推為 generic sandbox、gVisor、Kubernetes 或 Firecracker guarantee。

## Environment Receipt

| Component | Observed value |
| --- | --- |
| Host | macOS `26.4.0` / arm64 |
| Docker context | `orbstack` |
| Docker Client / API | `29.4.0` / `1.54` |
| Docker Engine | `29.4.0` / Linux arm64 |
| Engine kernel | `7.0.14-orbstack-00380-ga7e0a2dc9535` |
| containerd | `v2.2.2` |
| runc | `1.5.1` (`bb14dabeb7185bb72c8c86735d090dcb20f36587`) |
| Image digest | `python@sha256:94c50be2dc994b873b55bc123e95e6dbade08095b3dfd790f51c34de3f08cbb7` |

## Enforced Command Contract

`test_default_policy_compiles_to_default_deny_docker_flags` asserts：

```text
--network none
--read-only
--cap-drop ALL
--security-opt no-new-privileges
--pids-limit 32
--memory 64m
--cpus 0.50
--user 65534:65534
--tmpfs /tmp:rw,noexec,nosuid,size=16m
read-only corpus mount
explicit HOME/PATH only
immutable image digest
```

Docker accepted this command for all executed scenarios；若 flag 無效，`docker run` 不會得到各 corpus 的 expected result。Daemon default seccomp/AppArmor/SELinux 狀態沒有獨立 assertion，因此不列為 verified control。

## Test Command

```bash
python3 -m unittest discover \
  -s exercises/production-labs/lab-02-zero-trust-sandbox \
  -p 'test_*.py' -v
```

Result：exit code `0`；`Ran 10 tests in 7.124s`；`OK`。

## Machine-readable Scenario Receipt

```bash
python3 exercises/production-labs/lab-02-zero-trust-sandbox/run_lab.py
```

Result：exit code `0`。

| Scenario | Return | Observable stdout / state | Cleaned | Interpretation |
| --- | ---: | --- | --- | --- |
| success | 0 | `SANDBOX_OK` | true | success path removed container |
| forbidden filesystem | 0 | `FILESYSTEM_BLOCKED` | true | non-root read、read-only write、unmounted host path assertions passed |
| outbound network | 0 | `NETWORK_BLOCKED` | true | direct-IP TCP connect raised `OSError` under `network=none` |
| credential isolation | 0 | `CREDENTIAL_ABSENT` | true | mock host canary / production credential mount absent |
| memory exhaustion | 137 | no stdout | true | 256 MiB allocation stopped under 64 MiB limit |
| process exhaustion | 0 | `PIDS_BLOCKED` | true | attempt to create 100 child processes hit `OSError` under PID limit |
| explicit failure | 7 | no stdout | true | nonzero task仍 cleanup |
| timeout | 124 | `timed_out=true` | true | host timeout killed/removed infinite-loop container |
| residue writer | 0 | `RESIDUE_WRITTEN` | true | marker只寫 ephemeral tmpfs |
| next-run residue reader | 0 | `RESIDUE_ABSENT` | true | marker沒有跨 instance persistence |

Final inventory：

```bash
docker ps -a --filter name=agent-sandbox \
  --format '{{.ID}} {{.Names}} {{.Status}}'
```

Observed output：empty。

## TDD / Commit Receipt

| Increment | RED / gate evidence | GREEN commit |
| --- | --- | --- |
| Policy compiler | missing `sandbox_runner` import | `e16d1ce` |
| Execution + success cleanup | missing `run_script` API | `16a3bdb` |
| Filesystem/network/credential corpus | runtime negative assertions；host hook先拒絕含 sensitive filename 的 patch，改用 neutral fixture name | `7fd0a0c` |
| Resource/timeout/failure/residual cleanup | actual constrained container results | `67aae96` |
| Machine-readable receipt | scenario aggregation exits nonzero unless all expected decisions + cleanup pass | `8b21daa` |

## What Was Not Proven

- `network=none` case 沒開放任何 egress，因此沒驗證 allowlist proxy、DNS rebinding、redirect 或 Tool broker。
- mock canary absence 不等於 credential broker 已實作。
- `--cpus 0.50` 有 command assertion；沒有 scheduler fairness / CPU-throttle metric。
- `137` 與 Docker memory limit一致，但本報告沒有 kernel OOM event trace。
- Container shared-kernel escape、side channels、device/GPU、Unix sockets、output flood、storage forensic erasure 未測。
- Cleanup = runtime inventory absent + tmpfs marker absent；不是 physical media erasure proof。
- gVisor / Firecracker / Kubernetes / multi-host evidence是 `unknown`。

## First Divergence / Design Correction

一開始最容易把「Docker flags 存在」當阻擋證據。本 slice 將 static command contract 與 runtime negative evidence分開：前者證明 policy compiler 產生什麼，後者才證明指定 attack 在這個 daemon/image/kernel組合的結果。兩者都不能單獨證明 production安全。

## Next Action and Review

- Production promotion 前：用同一 corpus 並列跑 Docker/runc、gVisor、Firecracker candidate，增加 egress broker、output cap、lease/fencing 與 orchestrator-crash cleanup。
- `2026-08-12`：不看 note 重建 trust boundary / capability / cleanup state machine。
- `2026-08-18`：回答 [SD-AA-02 What-if](../../exercises/system-design/sd-02-zero-trust-agent-code-sandbox.md#13-what-if-pivot--review)，並加入至少一個新 attack case。
