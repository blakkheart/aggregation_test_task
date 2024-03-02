from datetime import datetime, timedelta
import json
import os

import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import Primary

load_dotenv()

MONGO_DB_ADRESS = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_ADRESS)
database = client.test_database
collection = database.test_collection


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


async def get_date(data: dict) -> str:
    '''Получение даты в формате ISO.'''

    year: int = data.get('_id').get('year', 0)
    month: int = data.get('_id').get('month', 1)
    day: int = data.get('_id').get('day', 1)
    hour: int = data.get('_id').get('hour', 0)
    week: int = data.get('_id').get('week', None)
    if week:
        date: str = (
            datetime(
                year=year, month=month,
                day=day, hour=hour
            ) + timedelta(weeks=week)
        ).isoformat()
        return date
    date: str = datetime(
        year=year, month=month,
        day=day, hour=hour
    ).isoformat()

    return date


async def raise_date(group_type: str, date: str) -> str:
    '''Увеличение даты в зависимости от типа группировки.'''

    if group_type == 'hour':
        raised_date: str = (datetime.fromisoformat(date)
                            + timedelta(hours=1)
                            ).isoformat()
    elif group_type == 'day':
        raised_date: str = (datetime.fromisoformat(date)
                            + timedelta(days=1)
                            ).isoformat()
    elif group_type == 'week':
        raised_date: str = (datetime.fromisoformat(date)
                            + timedelta(weeks=1)
                            ).isoformat()
    elif group_type == 'month':
        raised_date: str = (datetime.fromisoformat(date)
                            + relativedelta(months=1)
                            ).isoformat()
    return raised_date


@dp.message(Command('start'))
async def cmd_start(message: types.Message) -> None:
    '''Приветствие пользователя при команде /start.'''

    user_fullname: str = message.from_user.full_name
    user_id: int = message.from_user.id

    await message.answer(
        f'Hi [{user_fullname}](tg://user?id={str(user_id)})!',
        parse_mode='Markdown',
    )


@dp.message(F.text)
async def cmd_json(message: types.Message) -> None:
    '''Выдача агрегированных запросов пользователю.'''

    data_dict: dict = json.loads(message.text)
    group_type: str = data_dict.get('group_type')
    dt_from: str = data_dict.get('dt_from')
    dt_upto: str = data_dict.get('dt_upto')

    wrong_key_set = set()
    if not group_type:
        wrong_key_set.add('group_type')
    if not dt_from:
        wrong_key_set.add('dt_from')
    if not dt_upto:
        wrong_key_set.add('dt_upto')
    if wrong_key_set:
        await message.answer(f'Неверный ключ: {", ".join(wrong_key_set)}!')
        return

    if group_type == 'hour':
        pipeline: list[dict] = [
            {
                '$match': {'dt': {
                    '$gte': datetime.fromisoformat(dt_from),
                    '$lte': datetime.fromisoformat(dt_upto)
                }
                }
            },
            {
                '$project': {
                    'year': {'$year': "$dt"},
                    'month': {'$month': "$dt"},
                    'day': {'$dayOfMonth': '$dt'},
                    'hour': {'$hour': '$dt'},
                    'sum': {'$sum': '$value'},

                }
            },
            {
                '$group': {
                    '_id': {
                        'year': '$year',
                        'month': '$month',
                        'day': '$day',
                        'hour': '$hour',
                    },
                    'sum': {'$sum': '$sum'},
                }
            },
            {'$sort': {
                '_id': 1
            }
            }
        ]
    if group_type == 'day':
        pipeline: list[dict] = [
            {
                '$match': {'dt': {
                    '$gte': datetime.fromisoformat(dt_from),
                    '$lte': datetime.fromisoformat(dt_upto)
                }
                }
            },
            {
                '$project': {
                    'year': {'$year': "$dt"},
                    'month': {'$month': "$dt"},
                    'day': {'$dayOfMonth': '$dt'},
                    'sum': {'$sum': '$value'}

                }
            },
            {
                '$group': {
                    '_id': {
                        'year': '$year',
                        'month': '$month',
                        'day': '$day'
                    },
                    'sum': {'$sum': '$sum'},
                }
            },
            {'$sort': {
                '_id': 1
            }
            }
        ]
    if group_type == 'week':
        pipeline: list[dict] = [
            {
                '$match': {'dt': {
                    '$gte': datetime.fromisoformat(dt_from),
                    '$lte': datetime.fromisoformat(dt_upto)
                }
                }
            },
            {
                '$project': {
                    'year': {'$year': "$dt"},
                    'week': {'$isoWeek': '$dt'},
                    'sum': {'$sum': '$value'},

                }
            },
            {
                '$group': {
                    '_id': {
                        'year': '$year',
                        'week': '$week',
                    },
                    'sum': {'$sum': '$sum'},
                }
            },
            {'$sort': {
                '_id': 1
            }
            }
        ]
    if group_type == 'month':
        pipeline: list[dict] = [
            {
                '$match': {'dt': {
                    '$gte': datetime.fromisoformat(dt_from),
                    '$lte': datetime.fromisoformat(dt_upto)
                }
                }
            },
            {
                '$project': {
                    'year': {'$year': "$dt"},
                    'month': {'$month': "$dt"},
                    'sum': {'$sum': '$value'},

                }
            },
            {
                '$group': {
                    '_id': {
                        'year': '$year',
                        'month': '$month',
                    },
                    'sum': {'$sum': '$sum'},
                }
            },
            {'$sort': {
                '_id': 1
            }
            }
        ]

    result: dict[str, list] = {
        'dataset': [],
        'labels': []
    }
    async with await client.start_session() as s:
        async with s.start_transaction(
            read_concern=ReadConcern(level='majority'),
            read_preference=Primary(),
        ):
            async for data in collection.aggregate(pipeline):
                amount: int = data.get('sum')
                dataset: list = result.get('dataset')
                labels: list = result.get('labels')
                date = await get_date(data)

                while datetime.fromisoformat(date) > datetime.fromisoformat(dt_from):
                    dataset.append(0)
                    labels.append(dt_from)
                    dt_from: str = await raise_date(group_type, dt_from)

                dataset.append(amount)
                labels.append(date)
                dt_from: str = await raise_date(group_type, dt_from)

            date: str = await get_date(data)
            date: str = await raise_date(group_type, date)

            if datetime.fromisoformat(date) <= datetime.fromisoformat(dt_upto):
                dataset.append(0)
                labels.append(date)
                date: str = await raise_date(group_type, date)

    await message.answer(f'{json.dumps(result)}')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
