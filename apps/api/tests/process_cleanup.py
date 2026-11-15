"""Cleanup only descendants/groups created by this disposable browser test."""

import os
import signal
import subprocess
from pathlib import Path


def child_ids(identity, proc_root=Path("/proc")):
    result = set()
    for entry in (proc_root / str(identity) / "task").glob("*/children"):
        try:
            result.update(int(value) for value in entry.read_text().split())
        except FileNotFoundError:
            pass
    return sorted(result)


def terminate_owned(process):
    if process.poll() is not None:
        return  # Normal Node finally already closed its children; never inspect a reaped PID.
    if os.name == "nt":
        if process.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=10,
                check=False,
            )
    else:
        # Playwright may detach Chrome's process group. Discover descendants while
        # our Node parent is alive, without enumerating unrelated apps/profiles.
        pending = [process.pid]
        owned = []
        try:
            while pending:
                identity = pending.pop()
                if identity in owned:
                    continue
                try:
                    os.kill(identity, signal.SIGSTOP)  # Stop test-only forks before discovery.
                except ProcessLookupError:
                    continue
                owned.append(identity)
                if len(owned) > 512:
                    raise RuntimeError("Owned test process capacity exceeded")
                pending.extend(child_ids(identity))
        finally:
            for identity in reversed(owned):
                try:
                    os.kill(identity, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        # start_new_session=True establishes a private group for Node/Vite.
        if process.pid > 1 and process.pid != os.getpgrp():
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    if process.poll() is None:
        process.kill()
    process.communicate(timeout=5)
