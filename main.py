# это одна из первых версий бота
# пока он работает только на локальном сервере

import telebot
import os
from telebot import types
import mysql.connector

TOKEN = os.environ['TOKEN']
bot = telebot.TeleBot(os.getenv('TOKEN'))

connect_database = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password=os.getenv('PASSWORD'),
    database=os.getenv('DATABASE_NAME'),
    port='3306'

)

cursor = connect_database.cursor()

user_dict = {}


class User:
    def __init__(self, mood):
        self.mood = mood
        self.bad_things = None
        self.good_things = None


markup = types.InlineKeyboardMarkup(row_width=1)
start_button = types.InlineKeyboardButton("тык", callback_data='start')
markup.add(start_button)


@bot.message_handler(content_types=['text'])
def start_commands(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Привет! Я бот для отслеживания настроения. '
                                               'Напиши /help чтобы узнать, как я работаю или нажми на кнопку '
                                               'под сообщением, чтобы сразу начать', reply_markup=markup)
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Итак, отслеживать будем по трем параметрам. Все, что тебе нужно '
                                               'будет делать - это отвечать на сообщения')
        bot.send_message(message.from_user.id, 'Сначала я попрошу оценить твое сегодняшнее настроение по шкале '
                                               'от 1 до 10, где 1 - самое плохое, а 10 - самое хорошее. '
                                               'Пожалуйста, используй только целые числа.')
        bot.send_message(message.from_user.id, 'Вторым сообщением опиши, что тебя расстроило, разозлило, обидело - '
                                               'в общем, вызвало какие-либо негативные эмоции')
        bot.send_message(message.from_user.id, 'После придется вспомнить что-нибудь хорошее за прошедший день. '
                                               'Это может быть, например, вкусный кофе утром, а может - '
                                               'что-то масштабное')
        bot.send_message(message.from_user.id, 'Постарайся уместить ответы в несколько предложений.')
        bot.send_message(message.from_user.id, 'Чтобы начать, нажми на кнопку под этим сообщением', reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, 'Ничего не понял, извини, напиши /start или /help')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "start":
        bot.send_message(call.message.chat.id, 'Оцени свое сегодняшнее состояние по 10-балльной шкале')
        bot.register_next_step_handler(call.message, mood_registration)


def mood_registration(message):
    user_id = message.from_user.id
    mood = message.text
    user = User(mood)
    user_dict[user_id] = user
    if not mood.isdigit():
        bot.send_message(message.from_user.id, 'Пожалуйста, пиши цифрами')
        bot.register_next_step_handler(message, mood_registration)

    bot.send_message(message.from_user.id, 'Расскажи, что сегодня заставило тебя чувствовать себя хуже?')
    bot.register_next_step_handler(message, bad_things_registration)


def bad_things_registration(message):
    user_id = message.from_user.id
    bad_things = message.text
    user = user_dict[user_id]
    user.bad_things = bad_things
    bot.send_message(message.from_user.id, 'А теперь вспомни вещь, которая тебя сегодня порадовала')
    bot.register_next_step_handler(message, db_registration)


def db_registration(message):
    try:
        user_id = message.from_user.id
        user = user_dict[user_id]
        good_things = message.text
        bad_things = user.bad_things
        mood = user.mood
        sql = 'INSERT INTO records (user_id, mood, good_things, bad_things) VALUES (%s, %s, %s, %s)'
        one = (user_id, mood, good_things, bad_things)
        cursor.execute(sql, one)
        connect_database.commit()

        bot.send_message(message.from_user.id, 'Умничка!')
        bot.send_message(message.from_user.id, 'До завтра!')
    except Exception:
        bot.send_message(message.from_user.id, 'Ой, что-то пошло не так!')


bot.polling(none_stop=True, interval=0)
