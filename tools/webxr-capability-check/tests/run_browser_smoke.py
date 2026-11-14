"""Portable, dependency-free browser smoke. No browser download, personal profile or XR session."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from datetime import datetime, timezone, timedelta
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "tools/webxr-capability-check"
OUT = ROOT / ".local/browser-smoke"


def find_browser(environ=None, which=None, is_file=None):
    environ = os.environ if environ is None else environ
    which = shutil.which if which is None else which
    is_file = (lambda value: Path(value).is_file()) if is_file is None else is_file
    configured = environ.get("CHROME_BIN")
    if configured:
        candidate = which(configured) or configured
        return str(candidate) if is_file(candidate) else None
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "chrome.exe"):
        candidate = which(name)
        if candidate and is_file(candidate):
            return str(candidate)
    candidates = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/opt/google/chrome/chrome"]
    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        if environ.get(variable):
            candidates.append(str(Path(environ[variable]) / "Google/Chrome/Application/chrome.exe"))
    return next((value for value in candidates if is_file(value)), None)


def stop_browser(process):
    if process is None:
        return True
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            # Only the process tree created with our unique temporary profile, never a user's browser.
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=10, check=False)
        else:
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait(timeout=5)
    return process.poll() is not None


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    # Remove only stale output files from this tool, never profiles or arbitrary directories.
    (OUT / "checker-390.png").unlink(missing_ok=True)
    record = {
        "schema_version": 2,
        "executed_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds"),
        "environment": {"os": platform.system(), "release": platform.release(), "python": platform.python_version(), "ci": os.environ.get("CI") == "true"},
        "status": "NOT RUN", "scenarios": [],
        "hardware": {"status": "NOT RUN", "reason": "No physical AR/VR device tested."}
    }
    browser, node = find_browser(), shutil.which("node")
    server = process = temporary = None
    thread = None
    code = 2
    try:
        if not browser or not node:
            record["reason"] = "Không tìm thấy Chrome/Chromium hoặc Node >=22. Đặt CHROME_BIN hoặc thêm browser/Node vào PATH; runner không tự cài đặt."
            record["scenarios"] = [{"id": "runtime-discovery", "kind": "environment", "status": "NOT RUN", "expected": "An existing Chrome/Chromium executable and Node >=22 are available.", "actual": {"browser_found": bool(browser), "node_found": bool(node)}}]
        else:
            temporary = tempfile.TemporaryDirectory(prefix="profile-", dir=OUT)
            server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ASSETS)))
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            args = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--disable-background-networking", "--remote-debugging-address=127.0.0.1", "--remote-debugging-port=0", f"--user-data-dir={temporary.name}", "about:blank"]
            options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
            with (OUT / "browser-stderr.txt").open("w", encoding="utf-8") as log:
                process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=log, **options)
                active_port = Path(temporary.name) / "DevToolsActivePort"
                deadline = time.monotonic() + 15
                while not active_port.exists():
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError("Browser không khởi động được trong 15 giây; xem log local.")
                    time.sleep(0.1)
                port = int(active_port.read_text(encoding="utf-8").splitlines()[0])
                result = subprocess.run([node, str(Path(__file__).with_name("browser-driver.cjs")), f"http://localhost:{server.server_port}", str(port), str(OUT)], capture_output=True, text=True, encoding="utf-8", timeout=65, check=False)
                if result.returncode:
                    raise RuntimeError("Browser driver thất bại: " + result.stderr.strip()[:500])
                record.update(json.loads(result.stdout))
                code = 0 if record["status"] == "PASS" else 1
    except Exception as error:
        record.update(status="FAIL", reason=str(error))
        code = 1
    finally:
        cleanup = {}
        try:
            cleanup["browser_stopped"] = stop_browser(process)
        except Exception as error:
            cleanup["browser_stopped"] = False
            cleanup["error"] = str(error)
        if server:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        cleanup["server_closed"] = not thread or not thread.is_alive()
        try:
            if temporary:
                temporary.cleanup()
            cleanup["temporary_profile_removed"] = True
        except OSError:
            cleanup["temporary_profile_removed"] = False
        record["cleanup"] = cleanup
        if not all(cleanup.get(key) for key in ("browser_stopped", "server_closed", "temporary_profile_removed")):
            record.update(status="FAIL", reason="Cleanup không hoàn tất; xem local report.")
            code = 1
        (OUT / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
