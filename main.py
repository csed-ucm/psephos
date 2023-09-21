import subprocess
from src.unipoll_api.__version__ import version
from src.unipoll_api.utils import colored_dbg
from unipoll_api.utils import cli_args


def run(host="127.0.0.1", port=8000, reload=None):
    colored_dbg.info("University Polling API v{}".format(version))
    try:
        uvicorn_args: list[str] = ["--host", host, "--port", str(port)]
        if reload:
            uvicorn_args.append("--reload")
        subprocess.run(["uvicorn", "unipoll_api.app:app"] + uvicorn_args, cwd="src")
    except KeyboardInterrupt:
        colored_dbg.info("University Polling API stopped")


if __name__ == "__main__":
    args = cli_args.parse_args()
    run(args.host, args.port, args.reload)
