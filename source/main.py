import telebot
from funcs import get_token

TOKEN = get_token()
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Starting!")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, f'Got a message: {message.text}')


if __name__ == "__main__":
    bot.infinity_polling()
