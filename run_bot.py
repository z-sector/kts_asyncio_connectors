import sys

from bot.logger import run_logger
from bot.poller import run_poller
from bot.worker import run_worker

if __name__ == "__main__":
    assert len(sys.argv) > 1, "define cmd please"
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    if cmd == "poller":
        run_poller()
    elif cmd == "worker":
        run_worker()
    elif cmd == "logger":
        run_logger()
