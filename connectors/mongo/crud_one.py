import asyncio
import os
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


def get_client():
    return AsyncIOMotorClient(os.getenv("MONGO_URL"))


def get_db():
    return get_client().metaclass


def get_user_collection():
    return get_db().user


async def insert_user() -> ObjectId:
    document = {'first_name': 'Alexander', 'last_name': 'Opryshko'}
    result = await get_user_collection().insert_one(document)
    return result.inserted_id


async def find_user_by_id(user_id: ObjectId) -> Optional[dict]:
    document = await get_user_collection().find_one({'_id': user_id})
    return document


async def update_by_id(user_id: ObjectId) -> int:
    result = await get_user_collection().update_one({'_id': user_id}, {'$set': {'is_tutor': True}})
    return result.modified_count


async def delete_by_id(user_id: ObjectId) -> int:
    result = await get_user_collection().delete_one({'_id': user_id})
    return result.deleted_count


async def run():
    user_id = await insert_user()
    print('insert_user', user_id)
    user = await find_user_by_id(user_id)
    print('find_user_by_id', user)
    res = await update_by_id(user_id)
    print('update_by_id', res)
    user = await find_user_by_id(user_id)
    print('after update_by_id', user)
    # res = await delete_by_id(user_id)
    # print('delete_by_id', res)
    user = await find_user_by_id(user_id)
    print('after delete_by_id', user)


if __name__ == "__main__":
    asyncio.run(run())
