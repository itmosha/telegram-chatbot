import logging
import psycopg2
from aiogram import Bot, Dispatcher, executor, types
from funcs import get_token, get_answers, get_db_password

logging.basicConfig(level=logging.INFO)
bot = Bot(token=get_token())
dp = Dispatcher(bot)
conn = psycopg2.connect(dbname='telegram_bot', user='postgres', password=get_db_password(), host='localhost')
conn.autocommit=True

cursor = conn.cursor()
answers = get_answers()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(answers['START'])


@dp.message_handler()
async def process_message(message: types.Message):
    id = message.chat.id

    if id < 0:
        table_chat_name = f'table_{-id}'
    else:
        table_chat_name = f'table{id}'

    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_chat_name} ( message text NOT NULL );')
    cursor.execute(f'SELECT EXISTS ( SELECT 1 FROM {table_chat_name} WHERE message = \'{message.text}\')')

    if cursor:
        for row in cursor:
            if not row[0]:
                cursor.execute(f'INSERT INTO {table_chat_name} VALUES (\'{message.text}\');')
                await message.answer(answers['NEW'] + message.text)
            else:
                await message.answer(answers['ALREADY_KNOW'] + message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
