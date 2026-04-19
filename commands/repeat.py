from datetime import datetime, timedelta
from telebot import types
from math import floor
import pandas as pd
from random import randint

def repeat_0(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn0 = types.InlineKeyboardButton(text='Рус - Анг', callback_data='mode:0')
    btn1 = types.InlineKeyboardButton(text='Анг - Рус', callback_data='mode:1')
    btn2 = types.InlineKeyboardButton(text='Случайный', callback_data='mode:2')
    markup.add(btn0, btn1, btn2)
    bot.send_message(message.chat.id, 'В каждом режиме будем повторять?', reply_markup=markup)

def repeat_1(bot, call, way_to_data):
    from commands.get_packs_list import get_packs_list
    pack_list = get_packs_list(call.message, way_to_data)

    df = pd.read_csv(way_to_data, parse_dates=['date_of_repeat'],date_format='%Y-%m-%d',
                     converters={'pack_name': str, 'front_word': str, 'back_word': str})
    df = df.loc[df['tg_id'] == call.message.chat.id]  # оставляем колоды только этого пользователя
    df = df.loc[df['created_flag'] == False]    #убираем тех.инфу
    df = df[pd.to_datetime(df['date_of_repeat']) <= datetime.now()]  # отсеиваем по времени
    df = df[df['is_hidden']!=1]

    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in range(len(pack_list)):
        copy_df = df.loc[df['pack_name'] == pack_list[i]]   #считаем количество слов для каждой колоды

        btn = types.InlineKeyboardButton(text=f"{pack_list[i]} [{copy_df.shape[0]}]",
                                         callback_data=f'repeat:{call.data[-1]}:' + str(pack_list[i])) #call.data[-1] - режим повторения
        markup.add(btn)

    if len(pack_list) == 0:  # если нет колод
        btn = types.InlineKeyboardButton(text='+ создать колоду', callback_data='create_pack')
        markup.add(btn)
        bot.send_message(call.message.chat.id, 'У вас нет колод', reply_markup=markup)

    else:
        btn = types.InlineKeyboardButton(text=f'Все колоды [{len(df)}]', callback_data=f'repeat:{call.data[-1]}:random')
        markup.add(btn)
        bot.send_message(call.message.chat.id, 'Ваши колоды', reply_markup=markup)


def repeat_2(bot, message, flag, pack_name, way_to_data):
    df = pd.read_csv(way_to_data, parse_dates=['date_of_repeat'],date_format='%Y-%m-%d',converters={'pack_name': str, 'front_word': str, 'back_word': str})
    df = df.loc[df['tg_id'] == message.chat.id]  # оставляем колоды только этого пользователя
    if pack_name != 'random':
        df = df.loc[df['pack_name'] == pack_name]
    df = df.loc[df['created_flag'] == False]
    df = df[pd.to_datetime(df['date_of_repeat']) <= datetime.now()] #отсеиваем по времени
    df = df[df['is_hidden'] != 1]

    if  df.empty:
        if pack_name == 'random':
            bot.edit_message_text(f'В колодах больше нечего повторять', message.chat.id,
                                  message_id=message.message_id)
        else:
            bot.edit_message_text(f'В колоде {pack_name} нечего повторять', message.chat.id, message_id=message.message_id)
        return
    else:
        rand = randint(0, df.shape[0] - 1)
        row = df.iloc[rand]

        if flag == '1': first_word = row['front_word']
        elif flag == '0': first_word = row['back_word']
        else:
            c = randint(0, 1)
            if c == 1:
                first_word = row['front_word']
                flag = '2.1'
            else:
                first_word = row['back_word']
                flag = '2.0'

        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text='Проверить', callback_data=f"check:{flag}:{pack_name}:{row.name}") #row.name - имя(индекс) строки
        markup.add(btn)
        bot.edit_message_text(f"[{df.shape[0]}] Вспомните пару к слову\n\n<b>{first_word}\n \nㅤ</b>", message.chat.id,
                              message_id=message.message_id, parse_mode='HTML', reply_markup=markup)


def repeat_3(bot, call, way_to_data):
    message = call.message

    df = pd.read_csv(way_to_data, date_format='%Y-%m-%d', parse_dates=['date_of_repeat'],converters={'pack_name': str, 'front_word': str, 'back_word': str})

    df['date_of_repeat'] = pd.to_datetime(df['date_of_repeat'], format='%Y-%m-%d', errors='coerce')
    df = df.loc[df['tg_id'] == call.message.chat.id]  # оставляем колоды только этого пользователя
    flag, name, ind = call.data.replace('check:', '').split(':')
    if name != 'random':
        df = df.loc[df['pack_name'] == name]
    df = df.loc[df['created_flag'] == False]    #эта строка и ниже чисто, чтобы получить правильное количество строк
    df = df[pd.to_datetime(df['date_of_repeat']) <= datetime.now()]  # отсеиваем по времени
    rows = df.shape[0]
    row = df.loc[int(ind)]    #оставляем ту строку, у которой название как нужный индекс

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton(text='Легко', callback_data=f'easy:{flag}:{name}:{ind}')
    btn2 = types.InlineKeyboardButton(text='Средне', callback_data=f'medium:{flag}:{name}:{ind}')
    btn3 = types.InlineKeyboardButton(text='Сложно', callback_data=f'hard:{flag}:{name}:{ind}')
    btn4 = types.InlineKeyboardButton(text='Повторить еще раз', callback_data=f'again:{flag}:{name}:{ind}')
    btn5 = types.InlineKeyboardButton(text='Скрыть пару', callback_data=f'hide:{flag}:{name}:{ind}')
    markup.add(btn1, btn2, btn3, btn4, btn5)

    first, second = row['front_word'], row['back_word'] #задаем слова
    if flag[-1] != '1': first, second = second, first   #меняем их, если режим другой

    bot.edit_message_text(f"[{rows}] Проверка\n<b>{first}</b> - <b>{second}</b>\n"
                          f'Насколько легко было вспомнить?', message.chat.id, message_id=message.message_id,
                          parse_mode='HTML', reply_markup=markup)


def edit(bot, call, way_to_data):
    message = call.message

    df = pd.read_csv(way_to_data, parse_dates=['date_of_repeat'], date_format='%Y-%m-%d',converters={'pack_name': str, 'front_word': str, 'back_word': str, 'repeat_length': float})
    copy_df = df
    df = df.loc[df['tg_id'] == call.message.chat.id]  # оставляем колоды только этого пользователя
    react, flag, name, ind = call.data.split(':')
    if name != 'random':
        df = df.loc[df['pack_name'] == name]
    row = df.loc[int(ind)]

    repeat_length = row['repeat_length']    #получаем предыдущий промежуток

    #в первые 3 этапа повторения кнопки(кроме again) не имеют значения
    if react == 'easy' or (repeat_length < 5 and (react == 'medium' or react == 'hard')):
        new_gap = 1.5 * repeat_length + 1 #считаем по формуле y=2.5x+1, но в этой формуле отсчет от начала, а у меня
                                      #относительный, поэтому я вычитаю prev_gap

    elif react == 'medium' and repeat_length > 5:
        new_gap = (repeat_length - 1) / 1.5  #получаем предыдущее значение промежутка

    elif react == 'hard' and repeat_length > 5:
        new_gap = ((repeat_length - 1) / 1.5 - 1) / 1.5  #откатываем промежуток на два значения назад

    elif react == 'again': #в зависимости от того, какую оценку получило слово, будем менять интервал
        new_gap = 0 #сбрасываем промежуток
    else:
        bot.send_message(message.chat.id, "<code>Ошибка №8 в файле repeat</code>\nСообщить об ошибке @Tsygaika",
                         parse_mode='HTML')
        return

    try:
        copy_df.loc[int(ind), 'date_of_repeat'] = datetime.now().date() + timedelta(days=floor(new_gap))
        copy_df.loc[int(ind), 'repeat_length'] = new_gap
        copy_df.to_csv(way_to_data, index=False)  # сохраняем df

        repeat_2(bot, message, flag[0], name, way_to_data)

    except Exception as e:
        bot.send_message(message.chat.id, f"<code>Ошибка №9 в файле repeat</code>\nСообщить об ошибке @Tsygaika\n\n Код ошибки{e}",
                         parse_mode='HTML')