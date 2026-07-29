from telebot import TeleBot, types
from datetime import datetime
import pandas as pd

def quizlet_guide(bot, message, call_data):   #редактируем предыдущее сообщение и отправляем первый шаг из гайда
    call_data = call_data.split(':')[1] #получаем из call.data название колоды

    bot.edit_message_text('Что нужно добавить?\n✅Карточки Quizlet', message.chat.id, message_id=message.id,)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prev = types.InlineKeyboardButton(text='Назад', callback_data='prev_1:' + call_data)   #используем тег continue, чтобы
    btn_next = types.InlineKeyboardButton(text='Далее', callback_data='next_1:' + call_data)     #попасть обратно, к выбору
    markup.add(btn_prev, btn_next)

    bot.send_photo(message.chat.id, open('images/quizlet_guide_1.png', 'rb'),
                   caption=f'Откройте <a href="https://quizlet.com/">Quizlet</a> на ПК', parse_mode='HTML', reply_markup=markup)


def prev_1(bot, message, call_data):   #выходим из гайда
    call_data = call_data.split(':')[1]  # получаем из call.data название колоды

    bot.delete_message(message.chat.id, message.id)  # удаляем сообщение с первым шагом гайда

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='Слово', callback_data='add_word_to:' + call_data)
    btn2 = types.InlineKeyboardButton(text='Карточки из Quizlet', callback_data='add_quizlet_to:' + call_data)
    markup.add(btn1, btn2)

    i = 1   #так как сообщение с гайдом удаляется(визуально, но его айди все еще занято), а пользователь все еще
    while i < 11:                   #сможет нажать кнопку "карточки quizlet" пришлось сделать костыль
        try:
            bot.edit_message_text('Что нужно добавить?', message.chat.id, message_id=message.id - i,
                          reply_markup=markup)
            break
        except Exception:
            i += 1
            if i == 11:     #если он 10 раз удалил первый шаг гайда, то выводим ошибку
                bot.send_message(message.chat.id, "<code>Ошибка №3 в файле quizlet_guide</code>\nСообщить об ошибке @Tsygaika",
                                 parse_mode='HTML')

def next_1(bot, message, call_data):   #меняем на второй шаг гайда
    call_data = call_data.split(':')[1]  # получаем из call.data название колоды

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prev = types.InlineKeyboardButton(text='Назад', callback_data='prev_2:'  + call_data)
    btn_next = types.InlineKeyboardButton(text='Далее', callback_data='next_2:' + call_data)
    markup.add(btn_prev, btn_next)

    media = types.InputMediaPhoto(open("images/quizlet_guide_2.png", "rb"),
                                  caption='Нажмите на «•••» и далее выберите «Экспортировать»')
    bot.edit_message_media(media, message.chat.id, message.id, reply_markup=markup)


def prev_2(bot, message, call_data):   #возвращаемся к первому шагу гайда
    call_data = call_data.split(':')[1]  # получаем из call.data название колоды

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prev = types.InlineKeyboardButton(text='Назад', callback_data='prev_1:' + call_data)  # возвращаем кнопки как в шаге 1
    btn_next = types.InlineKeyboardButton(text='Далее', callback_data='next_1:' + call_data)
    markup.add(btn_prev, btn_next)

    media = types.InputMediaPhoto(open("images/quizlet_guide_1.png", "rb"),
                                  caption='Откройте <a href="https://quizlet.com/">Quizlet</a> на ПК', parse_mode='HTML')#возвращаем текст
    bot.edit_message_media(media, message.chat.id, message.id, reply_markup=markup)


def next_2(bot, message, call_data, way_to_data):   #меняем на третий шаг гайда
    call_data = call_data.split(':')[1]  # получаем из call.data название колоды

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prev = types.InlineKeyboardButton(text='Назад', callback_data='prev_3:' + call_data)
    markup.add(btn_prev)

    media = types.InputMediaPhoto(open("images/quizlet_guide_3.png", "rb"),
                                  caption='Нажмите на вариант «На выбор» и введите «=». Далее нажмите на кнопку «копировать текст» и отправьте текст боту')
    bot.edit_message_media(media, message.chat.id, message.id, reply_markup=markup)

    bot.register_next_step_handler(message, next_2_2, bot, call_data, way_to_data) #ждем текста от пользователя


def next_2_2(message, bot, call_data, way_to_data):   #пофиксить повторы
    bot_message = bot.send_message(message.chat.id, "<code>Ошибка №9 в файле quizlet_guide</code>\nСообщить об ошибке @Tsygaika",
                         parse_mode='HTML') #если ошибка здесь, значит проблема в 126 строке book.save('data.xlsx')

    pairs = message.text.split('\n')    #пары слов

    df = pd.read_csv(way_to_data, converters={'pack_name' : str,'front_word' : str,'back_word' : str})

    add_text = ', кроме(из-за неправильного формата):'    #если не все слова были введены правильно, то сообщим об этом
    for elem in pairs:
        elem = elem.split('=')  #разделяем на 2 слова
        if len(elem) == 2:
            if len(df.index): ind = df.index[-1] + 1    #кринж какой-то
            else: ind = 0
            df.loc[ind] = [message.chat.id, call_data, False, elem[0].replace(',','/'), elem[1].replace(',','/'), datetime.now().date(), 0, 0]

        else:   #если какая-то пара слов была введена неправильно
            add_text = add_text + '\n' +  '='. join(elem)   #добавляем к тексту исходный вид слов

    df.to_csv(way_to_data, index=False, encoding="utf-8-sig")  # сохраняем df

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='Добавить еще из Quizlet', callback_data='next_2_3:' + call_data)#тут надо сразу без гайда
    btn2 = types.InlineKeyboardButton(text='Вернуться к колодам', callback_data='add_cards')
    markup.add(btn1, btn2)

    if add_text == ', кроме(из-за неправильного формата):':
        add_text = ''   #если все пары слов были правильные, то текст добавлять не будем
    bot.edit_message_text('Были добавлены все слова' + add_text, bot_message.chat.id, message_id=bot_message.message_id,
                          reply_markup=markup)

def next_2_3(bot, message, call_data, way_to_data):
    bot.edit_message_text('Отправьте список слов в том же формате', message.chat.id, message_id=message.message_id)
    call_data = call_data.split(':')[1]  # получаем из call.data название колоды

    bot.register_next_step_handler(message, next_2_2, bot, call_data, way_to_data)