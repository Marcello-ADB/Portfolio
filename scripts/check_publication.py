"""Small publication guard for this synthetic repository; not a security audit."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SUFFIXES = {".py", ".md", ".json", ".svg", ".yml", ".yaml"}
ALLOWED_NAMES = {".gitignore", ".gitattributes", "LICENSE"}
PATTERNS = {
    "GitHub credential": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "JWT-shaped credential": re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"),
    "API credential": re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}"),
    "database URL with credentials": re.compile(r"(?:postgres(?:ql)?|mysql)://[^\s:]+:[^\s@]+@"),
    "local Windows path": re.compile(r"[A-Za-z]:[\\/](?:Users|Projetos)[\\/]", re.I),
    "private IPv4 address": re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b"),
}


def main():
    output = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT)
    paths = sorted({path for path in output.decode("utf-8").split("\0") if path})
    failures = []
    for name in paths:
        path = ROOT / name
        if not path.is_file():
            continue
        if path.name not in ALLOWED_NAMES and path.suffix not in ALLOWED_SUFFIXES:
            failures.append(f"{name}: file type not allowed in this public demo")
            continue
        if any(part.startswith(".env") or part in {"private", ".local-review", "backups"} for part in path.relative_to(ROOT).parts):
            failures.append(f"{name}: private/configuration path")
        if path.stat().st_size > 500_000:
            failures.append(f"{name}: unexpectedly large file")
        text = path.read_text(encoding="utf-8")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{name}: possible {label} (value suppressed)")
        if path.suffix == ".md":
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                destination = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                if not destination.is_relative_to(ROOT) or not destination.exists():
                    failures.append(f"{name}: missing or out-of-repository link {target}")
    if not paths:
        failures.append("No files found for review")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Publication guard passed: {len(paths)} files; local links resolved; no configured pattern matched.")
    print("This guard is limited. Human review and independent synthetic provenance remain necessary.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
