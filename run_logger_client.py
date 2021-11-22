import asyncio
import os
import sys

from run_logger import MetaclassLogger


async def run(level: str):
    async with MetaclassLogger(os.getenv("RABBITMQ_URL")) as logger:
        if level == 'info':
            await logger.info('run_logger_client.py', {'info': True})
        if level == 'critical':
            await logger.critical('run_logger_client.py', {'critical': True})


if __name__ == "__main__":
    lvl = sys.argv[1] if len(sys.argv) > 1 else "info"
    asyncio.run(run(lvl))
