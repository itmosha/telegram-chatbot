import logging
import psycopg2
from aiogram import Bot, Dispatcher, executor, types
from funcs import get_token, get_db_password, get_answers, get_config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=get_token())
dp = Dispatcher(bot)
conn = psycopg2.connect(dbname='telegram_bot', user='postgres', password=get_db_password(), host='localhost')
conn.autocommit = True

cursor = conn.cursor()
answers = get_answers()
config = get_config()
cursor.execute('CREATE TABLE IF NOT EXISTS botconfig ( \
               chat_id integer NOT NULL, \
               ans_chance integer NOT NULL CHECK ( ans_chance >= 0 AND ans_chance <= 100 ), \
               max_length integer NOT NULL CHECK ( max_length >= 0 AND max_length <= 500 ) );')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(answers['START'])

@dp.message_handler(commands=['memory'])
async def bot_memory(message: types.Message):
    id = message.chat.id
    table_chat_name = f'table_{-id}' if id < 0 else f'table{id}'
    cursor.execute(f'SELECT * FROM {table_chat_name};')

    result = answers['MEMORY']
    if not cursor.rowcount == 0:
        for row in cursor:
            result += '\n' + row[0]

    await message.answer(result)

@dp.message_handler(commands=['chance'])
async def change_chance(message: types.Message):
    if len(message.text.split()) > 1:
        new_chance = message.text.split()[1]

        if new_chance.isnumeric():
            new_chance = int(new_chance)
            if 0 <= new_chance <= 100:
                cursor.execute(f'UPDATE botconfig SET ans_chance = {new_chance} WHERE chat_id = {message.chat.id};')
                await message.answer(f'Шанс ответа был изменён на {new_chance}')
            else:
                await message.answer('Недействительное значение шанса ответа (0 - 100)')
        else:
            await message.answer('Введите значение шанса ответа (0 - 100)')
    else:
        cursor.execute(f'SELECT EXISTS ( SELECT 1 FROM botconfig WHERE chat_id = {message.chat.id} );')
        if not cursor.rowcount == 0:
            for row in cursor:
                if row[0]:
                    cursor.execute(f'SELECT ans_chance FROM botconfig WHERE chat_id = {message.chat.id};')
                    for row in cursor:
                        await message.answer(f'Текущий шанс ответа на сообщение: {row[0]}')
                else:
                    default_chance = config['answer_chance']
                    await message.answer(f'Текущий шанс ответа на сообщение: {default_chance}')

@dp.message_handler()
async def process_message(message: types.Message):
    id = message.chat.id
    table_sentences_name = f'table_{-id}' if id < 0 else f'table{id}'

    cursor.execute(f'SELECT EXISTS ( SELECT 1 FROM botconfig WHERE chat_id = {id});')

    if not cursor.rowcount == 0:
        for row in cursor:
            if not row[0]:
                cursor.execute(f'INSERT INTO botconfig VALUES ( {id}, 50, 100 );')


    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_sentences_name} ( message text NOT NULL );')
    cursor.execute(f'SELECT EXISTS ( SELECT 1 FROM {table_sentences_name} WHERE message = \'{message.text}\');')

    if not cursor.rowcount == 0:
        for row in cursor:
            if not row[0]:
                cursor.execute(f'INSERT INTO {table_sentences_name} VALUES (\'{message.text}\');')
                await message.answer(answers['NEW'] + message.text)
            else:
                await message.answer(answers['ALREADY_KNOW'] + message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
