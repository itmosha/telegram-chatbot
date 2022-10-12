import logging
from aiogram import Bot, Dispatcher, executor, types
from funcs import get_token


logging.basicConfig(level=logging.INFO)
bot = Bot(token=get_token())
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Welcome!')


@dp.message_handler()
async def process_message(message: types.Message):
    await message.answer(f'Got a message: {message.text}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
