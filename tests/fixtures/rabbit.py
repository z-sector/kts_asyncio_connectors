import os

import pytest

from connectors.rabbit.task.rmq_logger import LoggerConfig
from connectors.rabbit.task.rmq_worker import WorkerConfig


@pytest.fixture
async def worker_config():
    return WorkerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
        queue_name="worker_tests",
        capacity=2
    )


@pytest.fixture
async def logger_config():
    return LoggerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
        name="logger_tests",
    )
