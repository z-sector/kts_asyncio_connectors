import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient


def get_client():
    return AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://root:example@localhost:27017/"))


def get_db():
    return get_client().metaclass


def get_user_collection():
    return get_db().user


async def insert_many():
    bulk = []
    is_tutor = False
    for i in range(15):
        bulk.append(
            {'first_name': f'name{i}', 'last_name': f'last_name{i}', 'is_tutor': is_tutor}
        )
        is_tutor = not is_tutor
    await get_user_collection().insert_many(bulk)


async def find_using_cursor():
    cursor = get_user_collection().find({'is_tutor': {'$eq': True}}).sort('first_name')
    for document in await cursor.to_list(length=5):
        print(document)


async def find_using_async_for():
    cursor = get_user_collection().find({'is_tutor': {'$eq': True}}).sort('first_name')
    async for document in cursor:
        print(document)


async def run():
    await insert_many()
    await find_using_cursor()
    await find_using_async_for()


if __name__ == "__main__":
    asyncio.run(run())
