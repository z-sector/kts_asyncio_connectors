import os

import pytest

from connectors.rabbit.task.rmq_logger import LoggerConfig
from connectors.rabbit.task.rmq_worker import WorkerConfig


@pytest.fixture
async def worker_config():
    return WorkerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL"),
        queue_name="worker_tests",
        capacity=2
    )


@pytest.fixture
async def logger_config():
    return LoggerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL"),
        name="logger_tests",
    )
