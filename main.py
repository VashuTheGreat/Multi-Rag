from dotenv import load_dotenv

load_dotenv()

import subprocess
import sys

from src.core.logger import logger


def dev():
    logger.info("🚀 Starting Multi-RAG development server with hot-reload", host="0.0.0.0", port=7860)
    cmd = [
        "uvicorn",
        "api.app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "7860",
        "--reload",
    ]
    try:
        sys.exit(subprocess.run(cmd,check=False).returncode)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down server gracefully")
        sys.exit(0)


def start():
    logger.info("🚀 Starting Multi-RAG production server", host="0.0.0.0", port=7860)
    cmd = [
        "uvicorn",
        "api.app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "7860",
    ]
    try:
        sys.exit(subprocess.run(cmd,check=False).returncode)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down server gracefully")
        sys.exit(0)


if __name__ == "__main__":
    dev()
