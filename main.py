# это самая первая версия бота
# пока он работает только на локальном сервере
# позже будет добавлена база данных, возможность получить статистику за неделю и система ежедневных напоминаний

import telebot
import os
from telebot import types

TOKEN = os.environ['TOKEN']
bot = telebot.TeleBot(os.getenv('TOKEN'))

good_things = ''
bad_things = ''
mood = 0

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
        bot.send_message(message.from_user.id, 'Ничего не понятно')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "start":
        bot.send_message(call.message.chat.id, 'Чтобы убедиться, что мы друг друга понимаем - отправь любой стикер')
        bot.register_next_step_handler(call.message, what)


def what(message):
    bot.send_message(message.from_user.id, 'Оцени свое сегодняшнее состояние по 10-балльной шкале')
    bot.register_next_step_handler(message, mood_registration)


def mood_registration(message):
    global mood
    while mood == 0:
        try:
            mood = int(message.text)
        except Exception:
            bot.send_message(message.from_user.id, 'Это не цифры((')
            break
    if int(mood) > 0:
        bot.send_message(message.from_user.id, 'Расскажи, что сегодня заставило тебя чувствовать себя хуже?')
        bot.register_next_step_handler(message, bad_things_registration)


def bad_things_registration(message):
    global bad_things
    bad_things = message.text
    bot.send_message(message.from_user.id, 'А теперь вспомни вещь, которая тебя сегодня порадовала')
    bot.register_next_step_handler(message, good_things_registration)


def good_things_registration(message):
    global good_things
    good_things = message.text
    bot.send_message(message.from_user.id, 'Умничка!')
    bot.send_message(message.from_user.id, 'До завтра!')


bot.polling(none_stop=True, interval=0)
