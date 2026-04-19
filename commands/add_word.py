import pandas as pd
from telebot import TeleBot, types
from datetime import datetime

def add_word(bot, message, data, way_to_data):
    bot_message  = bot.send_message(message.chat.id, "Отправьте пару слов через =(вот так: <code>слово1=слово2</code>)", parse_mode='HTML')
    bot.register_next_step_handler(message, add_word_2, bot, data, bot_message, way_to_data)


def add_word_2(message, bot, data, bot_message, way_to_data):
    data = data.replace('add_word_to:', '')  # убираем префикс

    df = pd.read_csv(way_to_data, converters={'pack_name' : str,'front_word' : str,'back_word' : str})

    words = message.text.split('=')

    if len(words) != 2: #если пользователь ввел не два слова
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text='Ввести еще раз', callback_data='add_word_to:' + data)
        markup.add(btn)
        bot.edit_message_text('Вы ввели слова в неверном формате', bot_message.chat.id,
                              message_id=bot_message.message_id, reply_markup=markup)
        return

    if len(df.index): ind = df.index[-1] + 1 #определяем индекс последнего элемента(после удаления пары он не равен длине dataframe)
    else: ind = 0
    df.loc[ind] = [message.chat.id, data, False, words[0].replace(',','/'), words[1].replace(',','/'), datetime.now().date(), 0, 0]   #добавляем в df
    df.to_csv(way_to_data, index=False, encoding="utf-8-sig")  # сохраняем df

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='Добавить еще пару', callback_data='add_word_to:' + data)
    btn2 = types.InlineKeyboardButton(text='Вернуться к колодам', callback_data='add_cards')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f"Пара слов {words[0]} - {words[1]} была добавлена в колоду {data}", reply_markup=markup)