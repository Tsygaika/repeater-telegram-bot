from telebot import TeleBot, types
from dotenv import load_dotenv
import os
import platform

from background import keep_alive

load_dotenv()
bot = TeleBot(os.getenv("BOT_TOKEN"))

# if platform.node() == "Alexey":
way_to_data = 'data/data_repeater.csv'
way_to_wordix_db = 'data/data_wordix.csv'
# else:
#     way_to_data = '/data/data_repeater.csv'
#     way_to_wordix_db = '/data/data_wordix.csv'

################ КОМАНДЫ ################ КОМАНДЫ ################
@bot.message_handler(commands=["start"])
def start(message):    
    markup = types.InlineKeyboardMarkup(row_width = 1)
    btn1 = types.InlineKeyboardButton(text = 'Добавить карточки', callback_data = 'add_cards')
    markup.add(btn1)
    bot.send_message(message.chat.id, f"{message.from_user.first_name}, добро пожаловать в бота!"
                                      f"\nВот основные команды: /help\nДобавляй слова и повторяй их. Также ты можешь "
                                      f"отправлять мне слова, а я буду их записывать и считать кол-во", reply_markup = markup)

@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "Список команд\n\n/add - добавить карточки в колоду\n/create - создать колоду"
                                      "\n/watch - посмотреть колоду\n/repeat - повторить слова\n/delpair - удалить пару слов\n"
                                      "/download - скачать слова из всех колод\n\n/view 50 - посмотреть список слов, "
                                      "отправленных в чат\n /pop 10 - удалить топ 10 слов по частоте")

@bot.message_handler(commands=["version"])
def version(message):
    bot.send_message(message.chat.id, 'Версия бота: 31072025')

@bot.message_handler(commands=["add"])  #добавить карточку
def add(message):
    from commands.add_cards import add_cards
    add_cards(bot, message, way_to_data)

@bot.message_handler(commands=["create"])   #создать список
def create(message):
    from commands.create_pack import create_pack
    create_pack(bot, message, way_to_data)

@bot.message_handler(commands=["watch"])    #посмотреть список карточек
def watch(message):
    from commands.watch import watch
    watch(bot, message, way_to_data)

@bot.message_handler(commands=["repeat"])   #повторить карточки
def repeat(message):
    from commands.repeat import repeat_0
    repeat_0(bot, message)

@bot.message_handler(commands=["delpair"])   #удалить пару карточек
def delpair(message):
    from commands.delete_pair import delete_pair
    delete_pair(bot, message, way_to_data)

@bot.message_handler(commands=["showdata"])   #показать всю информацию о карточках в колоде
def showdata(message):
    from commands.showdata import showdata
    showdata(bot, message, way_to_data)

@bot.message_handler(commands=["download","load"])   #скачать все слова для конкретного пользователя
def download(message):
    from commands.download import download
    download(bot, message, way_to_data)

@bot.message_handler(commands=['pop'])  #удалить слово из списка wordix
def pop(message):
    from commands.wordix.pop import pop
    pop(bot, message, way_to_wordix_db)

@bot.message_handler(commands=['view']) #посмотреть слова в списке wordix
def view(message):
    from commands.wordix.view import view
    view(bot, message, way_to_wordix_db)

################ ОБРАБОТКА КНОПОК ################
@bot.callback_query_handler(func = lambda call:True)
def buttons(call):
    bot.answer_callback_query(call.id)  #убираем загрузку на кнопке

    if call.data == 'add_cards':
        from commands.add_cards import add_cards
        add_cards(bot, call.message, way_to_data)

    elif call.data == 'create_pack':
        from commands.create_pack import create_pack
        create_pack(bot, call.message, way_to_data)

    elif call.data.startswith('add_word_to:'):  #если строка начинается с 'add_word', то нужно добавить слово в колоду
        from commands.add_word import add_word
        add_word(bot, call.message, call.data, way_to_data)

    #начало гайда в quizlet
    elif call.data.startswith('add_quizlet_to:'):
        from commands.quizlet_guide import quizlet_guide
        quizlet_guide(bot, call.message, call.data)

    elif call.data.startswith('prev_1:'):
        from commands.quizlet_guide import prev_1
        prev_1(bot, call.message, call.data)

    elif call.data.startswith('next_1:'):
        from commands.quizlet_guide import next_1
        next_1(bot, call.message, call.data)

    elif call.data.startswith('next_2:'):
        from commands.quizlet_guide import next_2
        next_2(bot, call.message, call.data, way_to_data)

    elif call.data.startswith('prev_2:'):
        from commands.quizlet_guide import prev_2
        prev_2(bot, call.message, call.data)

    elif call.data.startswith('next_2_3:'):
        from commands.quizlet_guide import next_2_3
        next_2_3(bot, call.message, call.data, way_to_data)

    elif call.data.startswith('prev_3:'):
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id) #из-за того, что мы ждали сообщение от
                                    #пользователя, но он вернулся, нам нужно перестать ждать от него сообщение
        from commands.quizlet_guide import next_1   #назад с 3 шага то же самое, что вперед с 1 шага
        next_1(bot, call.message, call.data)

    elif call.data.startswith('packname:'):
        markup = types.InlineKeyboardMarkup(row_width=1)
        call_data = call.data.replace('packname:', '') #убираем 'packname:' и сохраняем текст в call.data
        btn1 = types.InlineKeyboardButton(text='Слово', callback_data= 'add_word_to:' + call_data)  # сохраним также
        btn2 = types.InlineKeyboardButton(text='Карточки из Quizlet', callback_data='add_quizlet_to:' + call_data)  # название колоды
        markup.add(btn1, btn2)
        bot.edit_message_text('Что нужно добавить?', call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=markup)

    elif call.data.startswith('watch:'):
        from commands.watch import open_pack
        open_pack(bot, call, way_to_data)

    elif call.data.startswith('showdata:'):
        from commands.showdata import open_pack
        open_pack(bot, call, way_to_data)

    elif call.data.startswith('mode:'):
        from commands.repeat import repeat_1
        if call.data == 'mode:0': regime = 'Рус - Анг'
        else: regime = 'Анг - Рус'
        bot.edit_message_text(f'Был выбран режим: {regime}', call.message.chat.id, message_id=call.message.message_id)
        repeat_1(bot, call, way_to_data)

    elif call.data.startswith('repeat:'):
        from commands.repeat import repeat_2
        flag, packname = call.data.replace('repeat:', '').split(':')
        repeat_2(bot, call.message, flag, packname, way_to_data)

    elif call.data.startswith('check:'):
        from commands.repeat import repeat_3
        repeat_3(bot, call, way_to_data)

    elif call.data.startswith('delete:'):
        from commands.delete_pair import delete_pair_2
        delete_pair_2(bot, call, way_to_data)

    elif call.data.startswith(('easy:', 'medium:', 'hard:', 'again:')):
        from commands.repeat import edit
        edit(bot, call, way_to_data)

    else:   #иначе это названия его колод
        bot.send_message(call.message.chat.id, "произошло исключение")
        print('ИСКЛЮЧЕНИЕ')

#TEXT MESSAGES PROCESSING для WORDIX
@bot.message_handler(content_types=['text'])
def text_received(message):
    text = message.text
    if "/" in text:
        bot.send_message(message.chat.id, "Неизвестная команда")

    else:
        from commands.wordix.add_word import add_word
        add_word(bot, message, way_to_wordix_db)

#### ПРОВЕРКА РАБОТЫ САЙТА ПРОЕКТНОГО ОФИСА
# import json
# import requests
#
# URL = 'https://cabinet.miem.hse.ru/catalog'
#
# def checker():
#     with open("config.json", "r") as f: #открываем config
#         state = json.load(f)
#
#     if URL not in state or not state[URL]: #проверяем, что мы еще не сообщили о работе сайта
#         try:
#             requests.get(URL, timeout = 5) #кидаем запрос
#
#             state[URL] = True #если исключение не вылетело, то меняем состояние на True
#             with open("config.json", "w") as f: #и записываем
#                 json.dump(state, f, indent=4)
#
#             bot.send_message(875771161, f"Сайт {URL} работает!")
#
#         except requests.ConnectionError:
#             pass

###СОХРАНЕНИЕ БД
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()

def save_db():
    bot.send_document(-4580716050, open(way_to_data, 'rb'))

scheduler.add_job(save_db, 'cron', hour=22, minute=0)

# #webhook####################### НЕ ТРОГАТЬ!!!###################
# keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
# bot.infinity_polling(none_stop=True)
# #запуск бота

def start_bot():
    bot.infinity_polling()  # Запуск в режиме long polling

if __name__ == "__main__":
    start_bot()  # Для тестирования одного бота