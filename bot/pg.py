from dataclasses import dataclass
from typing import Optional, Tuple

import asyncpg


@dataclass
class PgConfig:
    url: str


class Pg:
    """
    Pg класс позволяет выполнять запросы к базе данных postgres
    логику работы с базом можно было бы оставить внутри worker
    но в программировании является хорошей практикой разделять код на логические части
    поэтому взаимодействие с БД будет осуществлять через этот класс
    """
    def __init__(self, config: PgConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
