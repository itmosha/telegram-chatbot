import logging
from aiogram import Bot, Dispatcher, executor, types
from funcs import get_token, get_answers

logging.basicConfig(level=logging.INFO)
bot = Bot(token=get_token())
dp = Dispatcher(bot)
answers = get_answers()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(answers["START"])


@dp.message_handler()
async def process_message(message: types.Message):
    await message.answer(answers["DEFAULT"] + message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
