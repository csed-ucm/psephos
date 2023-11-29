import sys
sys.path.append("src")
from unipoll_api import entry_points  # noqa: E402


if __name__ == "__main__":
    entry_points.cli_entry_point()
