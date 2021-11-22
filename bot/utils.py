import functools
import logging


def log_exceptions(func):
    @functools.wraps(func)
    async def _wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            raise e
    return _wrapper
