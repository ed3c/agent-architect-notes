import subprocess


processes = []
try:
    for _ in range(100):
        processes.append(subprocess.Popen(["/usr/bin/sleep", "2"]))
except OSError:
    print("PIDS_BLOCKED")
else:
    raise AssertionError("PID limit allowed 100 child processes")
finally:
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait()
