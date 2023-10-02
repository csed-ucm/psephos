import sys
sys.path.append("src")
from unipoll_api import app  # noqa: E402


if __name__ == "__main__":
    app.run()
