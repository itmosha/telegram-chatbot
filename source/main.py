import logging
import psycopg2
import random
import markovify
from aiogram import Bot, Dispatcher, executor, types
from getters import get_token, get_db_password, get_answers, get_config
from strings import get_table_chat_name

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


@dp.message_handler(commands=['info'])
async def start(message: types.Message):
    await message.answer(answers['INFO'], parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['memory'])
async def bot_memory(message: types.Message):
    table_chat_name = get_table_chat_name(message)
    cursor.execute(f'SELECT count(*) FROM {table_chat_name};')

    if not cursor.rowcount == 0:
        for row in cursor:
            await message.answer(answers['MEMORY'] + str(row[0]))


@dp.message_handler(commands=['clear'])
async def clear_memory(message: types.Message):
    table_chat_name = get_table_chat_name(message)

    cursor.execute(f'DELETE FROM {table_chat_name};')
    await message.answer(answers['MEMORY_CLEARED'])


@dp.message_handler(commands=['chance'])
async def change_chance(message: types.Message):
    if len(message.text.split()) > 1:
        new_chance = message.text.split()[1]

        if new_chance.isnumeric():
            new_chance = int(new_chance)
            if 0 <= new_chance <= 100:
                cursor.execute(f'UPDATE botconfig SET ans_chance = {new_chance} WHERE chat_id = {message.chat.id};')
                await message.answer(answers['CHANCE_CHANGED'] + str(new_chance))
            else:
                await message.answer(answers['CHANCE_INVALID'])
        else:
            await message.answer(answers['CHANCE_INVALID'])
    else:
        cursor.execute(f'SELECT EXISTS ( SELECT 1 FROM botconfig WHERE chat_id = {message.chat.id} );')
        if not cursor.rowcount == 0:
            for row in cursor:
                if row[0]:
                    cursor.execute(f'SELECT ans_chance FROM botconfig WHERE chat_id = {message.chat.id};')
                    for row in cursor:
                        await message.answer(answers['CHANCE_CURRENT'] + row[0])
                else:
                    default_chance = config['answer_chance']
                    await message.answer(answers['CHANCE_CURRENT'] + str(default_chance))


@dp.message_handler()
async def process_message(message: types.Message):
    id = message.chat.id
    table_chat_name = get_table_chat_name(message)

    cursor.execute(f'SELECT EXISTS ( SELECT 1 FROM botconfig WHERE chat_id = {id});')

    if not cursor.rowcount == 0:
        for row in cursor:
            if not row[0]:
                cursor.execute(f'INSERT INTO botconfig VALUES ( {id}, 50, 100 );')

    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_chat_name} ( message text NOT NULL );')
    cursor.execute(f'SELECT 1 FROM {table_chat_name} WHERE message = \'{message.text}\';')

    if cursor.rowcount == 0:
        cursor.execute(f'INSERT INTO {table_chat_name} VALUES (\'{message.text}\');')

    answer_chance = random.randint(0, 99)
    current_chat_chance = config['answer_chance']

    cursor.execute(f'SELECT ans_chance FROM botconfig WHERE chat_id = {id};')
    if cursor.rowcount > 0:
        for row in cursor:
            current_chat_chance = row[0]

    if answer_chance < current_chat_chance:
        # Generate sentence

        cursor.execute(f'SELECT * FROM {table_chat_name};')
        all_messages = ''
        for row in cursor:
            all_messages += row[0] + '\n'
        all_messages = all_messages.replace("\n\n", "\n")
        all_messages = all_messages.lower().strip()

        text_model = markovify.Text(all_messages)
        bot_answer = text_model.make_sentence(tries=100)

        if bot_answer is None:
            print("Random: ")
            bot_answer = random.choice(all_messages.splitlines())

        print(bot_answer)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
