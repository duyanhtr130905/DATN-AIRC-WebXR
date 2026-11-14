"""Run existing Chrome headless on loopback; no downloads or hardware claims."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import subprocess
import json
import re
import html
import sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / 'tools/webxr-capability-check'
CHROME = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
OUT = ROOT / '.local/browser-smoke'
OUT.mkdir(parents=True, exist_ok=True)
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(ASSETS)))
Thread(target=server.serve_forever, daemon=True).start()
base = f'http://localhost:{server.server_port}'
try:
    version = subprocess.check_output(['powershell', '-NoProfile', '-Command', f"(Get-Item -LiteralPath '{CHROME}').VersionInfo.ProductVersion"], text=True).strip()
    args = [str(CHROME), '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-background-networking', f'--user-data-dir={OUT / "profile"}', '--dump-dom', '--virtual-time-budget=15000', base + '/tests/browser-smoke.html']
    process = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=50)
    (OUT / 'dom.html').write_text(process.stdout, encoding='utf-8')
    (OUT / 'stderr.txt').write_text(process.stderr, encoding='utf-8')
    match = re.search(r'<pre id="result">(.*?)</pre>', process.stdout, re.S)
    result = html.unescape(match.group(1)) if match else 'FAIL: missing browser result'
    record = {'date': '2026-11-14', 'browser': 'Chrome headless', 'version': version, 'gpu': 'disabled; no performance evidence', 'result': result, 'exit_code': process.returncode}
    (OUT / 'result.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False, indent=2))
    if process.returncode != 0 or not result.startswith('PASS'):
        raise SystemExit(1)
finally:
    server.shutdown()
    server.server_close()
