import re
from pathlib import Path

WORKFLOWS = Path(".github/workflows")
USES = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)(?:\s+#.*)?$")
PINNED = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")


def main() -> None:
    violations: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = USES.match(line)
            if not match:
                continue
            reference = match.group(1)
            if reference.startswith("./"):
                continue
            if not PINNED.fullmatch(reference):
                violations.append(f"{path}:{number}: action is not SHA-pinned: {reference}")

    if violations:
        raise SystemExit("\n".join(violations))
    print("OK: all external GitHub Actions are pinned to full commit SHAs")


if __name__ == "__main__":
    main()
