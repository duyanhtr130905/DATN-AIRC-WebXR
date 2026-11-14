"""Read-only M0 link, UTF-8, privacy-pattern and checker resource checks."""
from pathlib import Path
import re
import sys
import struct
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.local', 'node_modules', '__pycache__', '.venv'}
files = [p for p in ROOT.rglob('*') if p.is_file() and not EXCLUDED.intersection(p.relative_to(ROOT).parts)]
errors = []
links = 0
patterns = [r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{40,}', r'AKIA[0-9A-Z]{16}', r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
for path in files:
    if path.suffix.lower() == '.png':
        data = path.read_bytes()
        if path.relative_to(ROOT).as_posix() != 'docs/evidence/checker-390.png':
            errors.append(f'Unexpected binary asset: {path.relative_to(ROOT)}')
        elif len(data) > 200_000 or data[:8] != b'\x89PNG\r\n\x1a\n' or len(data) < 24:
            errors.append('Checker screenshot invalid or larger than 200 KB')
        elif struct.unpack('>I', data[16:20])[0] != 390:
            errors.append('Checker screenshot must be 390 pixels wide')
        continue
    try:
        content = path.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        errors.append(f'Non UTF-8 file: {path.relative_to(ROOT)}')
        continue
    for pattern in patterns:
        if re.search(pattern, content):
            errors.append(f'Possible secret: {path.relative_to(ROOT)} (value omitted)')
    if path.suffix == '.md':
        content = re.sub(r'```.*?```', '', content, flags=re.S)
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', content):
            target = target.strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith('#'):
                continue
            links += 1
            local = (path.parent / unquote(parsed.path)).resolve()
            if not local.is_relative_to(ROOT) or not local.exists():
                errors.append(f'Broken/escaping local link: {path.relative_to(ROOT)} -> {target}')

class Resources(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'href') and value and not value.startswith('data:'):
                if urlsplit(value).scheme or value.startswith('//'):
                    errors.append('Checker uses remote resource')
                elif not (ROOT / 'tools/webxr-capability-check' / value).exists():
                    errors.append(f'Missing checker resource: {value}')
Resources().feed((ROOT / 'tools/webxr-capability-check/index.html').read_text(encoding='utf-8'))
js = (ROOT / 'tools/webxr-capability-check/checker.js').read_text(encoding='utf-8')
for forbidden in [r'\bfetch\s*\(', r'\bXMLHttpRequest\b', r'\bWebSocket\s*\(', r'\brequestSession\s*\(', r'\bgetUserMedia\s*\(', r'\bsendBeacon\s*\(', r'\b(?:localStorage|sessionStorage)\b']:
    if re.search(forbidden, js):
        errors.append('Checker contains prohibited side-effect API')
print(f'Checked {len(files)} repository files (UTF-8 or allowlisted PNG) and {links} local Markdown links; secret patterns and checker resources inspected.')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('PASS — limited pattern scan, not a full security audit; external URLs checked separately in source research.')
