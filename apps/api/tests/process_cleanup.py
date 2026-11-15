"""Cleanup only descendants/groups created by this disposable browser test."""

import os
import signal
import subprocess
from pathlib import Path


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
        while pending:
            identity = pending.pop()
            if identity in owned:
                continue
            owned.append(identity)
            if len(owned) > 512:
                raise RuntimeError("Owned test process capacity exceeded")
            children = Path(f"/proc/{identity}/task/{identity}/children")
            try:
                pending.extend(int(value) for value in children.read_text().split())
            except FileNotFoundError:
                pass
        if process.poll() is None:
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
