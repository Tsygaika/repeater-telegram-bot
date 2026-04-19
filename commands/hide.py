from telebot import types
import pandas as pd

def get_two_words(message): #выдает первые 2 форматированных слова
    entities = sorted(message.entities, key=lambda e: e.offset)
    ent1, ent2 = entities[0], entities[1]
    first = message.text[ent1.offset:ent1.offset + ent1.length]
    second = message.text[ent2.offset:ent2.offset + ent2.length]
    return first, second


def hide_1(bot, call):
    message = call.message
    call_data_info = call.data.replace('hide:', '')
    first, second = get_two_words(message)

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton(text='Скрыть', callback_data=f'hide_2:{call_data_info}')
    btn2 = types.InlineKeyboardButton(text='Отмена', callback_data=f'cancel:{call_data_info}')
    markup.add(btn1, btn2)

    bot.edit_message_text(f"Вы уверены, что хотите скрыть пару <b>{first}</b> - <b>{second}</b>?\nПосле скрытия"
                          f" она не будет попадаться в колоде.\n/hidden - вернуть скрытые пары",
                          message.chat.id, message_id=message.message_id, parse_mode='HTML', reply_markup=markup)

def hide_2(bot, call, way_to_data):
    call_data_info = call.data.replace('hide_2:', '')

    df = pd.read_csv(way_to_data, parse_dates=['date_of_repeat'], date_format='%Y-%m-%d',
                     converters={'pack_name': str, 'front_word': str, 'back_word': str, 'repeat_length': float})

    ind = call.data.split(':')[-1]
    df.loc[int(ind), 'is_hidden'] = 1

    df.to_csv(way_to_data, index=False, encoding='utf-8-sig')

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn = types.InlineKeyboardButton(text='Продолжить повторение', callback_data=f"continue:{call_data_info}")
    markup.add(btn)

    first, second = get_two_words(call.message)
    bot.edit_message_text(f"Пара {first} - {second} скрыта", call.message.chat.id, message_id=call.message.message_id,
                    reply_markup=markup)

def cancel(bot, call, way_to_data):
    call.data = call.data.replace('cancel', 'check')
    from commands.repeat import repeat_3
    repeat_3(bot, call, way_to_data)


def add_is_hidden_column(bot, message, way_to_data):
    df = pd.read_csv(way_to_data, parse_dates=['date_of_repeat'], date_format='%Y-%m-%d',
                     converters={'pack_name': str, 'front_word': str, 'back_word': str, 'repeat_length': float})

    if 'is_hidden' in df.columns:
        return

    df['is_hidden'] = 0
    df.to_csv(way_to_data, index=False)
    bot.send_message(message.chat.id, 'Новая колонка добавлена')


def show_hidden(bot, message, way_to_data):
    df = pd.read_csv(way_to_data, parse_dates=['date_of_repeat'], date_format='%Y-%m-%d',
                     converters={'pack_name': str, 'front_word': str, 'back_word': str, 'repeat_length': float})
    df = df.loc[df['tg_id'] == message.chat.id]  # оставляем колоды только этого пользователя
    df = df.loc[df['created_flag'] == False]
    df = df[df['is_hidden'] == 1]

    text = 'Скрытые пары из всех колод:\n\n'
    for i, row in df.iterrows():
        text += f'{i} {row['front_word']} - {row['back_word']}\n'

    text += '\nЧтобы снова показывать пару, напишите: /show [число, которое стоит перед парой]'

    while len(text) > 0:
        bot.send_message(message.chat.id, text[:4000])
        text = text[4000:]

def show_pair(bot, message, ind, way_to_data):
    df = pd.read_csv(way_to_data, parse_dates=['date_of_repeat'], date_format='%Y-%m-%d',
                     converters={'pack_name': str, 'front_word': str, 'back_word': str, 'repeat_length': float})

    copy_df = df.copy()
    copy_df = copy_df.loc[copy_df['tg_id'] == message.chat.id]
    copy_df = copy_df.loc[copy_df['created_flag'] == False]
    copy_df = copy_df[copy_df['is_hidden'] == 1]

    if ind not in copy_df.index:
        bot.send_message(message.chat.id, "Такого числа нет в списке скрытых пар")
        return

    df.loc[ind, 'is_hidden'] = 0

    df.to_csv(way_to_data, index=False, encoding='utf-8-sig')

    bot.send_message(message.chat.id, f"Пара {df.loc[ind, 'front_word']} - {df.loc[ind, 'back_word']} будет снова встречаться в колодах")