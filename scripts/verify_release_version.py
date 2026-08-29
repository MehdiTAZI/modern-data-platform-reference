import sys
import tomllib
from pathlib import Path


def project_version() -> str:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_release_version.py <version-or-vtag>")
    requested = sys.argv[1].removeprefix("v")
    actual = project_version()
    if requested != actual:
        raise SystemExit(f"release version {requested!r} does not match pyproject {actual!r}")
    print(f"OK: release version {actual}")


if __name__ == "__main__":
    main()
