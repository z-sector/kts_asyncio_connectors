import os

import pytest

from bot.logger import BotLoggerConfig
from bot.pg import PgConfig
from bot.poller import PollerConfig
from bot.worker import BotConfig
from connectors.rabbit.task.rmq_worker import WorkerClientConfig, WorkerConfig


@pytest.fixture
async def poller_config():
    return PollerConfig(
        worker_client_config=WorkerClientConfig(
            rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
            queue_name="bot_poller_tests"
        ),
        logger_config=BotLoggerConfig(
            rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
            mongo_url=os.getenv("MONGO_URL", "mongodb://root:example@localhost:27017/"),
            name="bot_logger_tests",
            mongo_db="bot_tests"
        )
    )


@pytest.fixture
async def bot_config(tg_token):
    worker_config = WorkerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
        queue_name="bot_poller_tests",
        capacity=5
    )
    return BotConfig(
        worker_config=worker_config,
        pg_config=PgConfig(url=os.getenv("POSTGRES_DSN", "postgres://postgres:postgres@localhost:45432/postgres"))
    )
