# mypy: allow-untyped-calls
import subprocess  # nosec B404
import sys

if sys.version_info[:2] >= (3, 8):
    import importlib.metadata as metadata
else:
    import importlib_metadata as metadata


def find_my_version() -> str:
    try:
        # installed version
        return str(metadata.version("molskaten")).strip("'")
    except Exception:
        # git / non-installed version
        return find_git_version()


def find_git_version() -> str:
    result = subprocess.run(  # nosec B603 B607
        ["git", "describe", "--tags", "--match", "v*.*.*"],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        shell=False,
    )

    if result.returncode == 0:
        output = result.stdout.decode("utf-8").lstrip("v").rstrip()
    else:
        output = "0.0.0"

    return output


if __name__ == "__main__":
    print(find_my_version())
