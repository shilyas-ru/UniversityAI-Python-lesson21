from os.path import exists
from random import random

import telebot
from telebot import types

# from telegram import ParseMode

# Ссылки на материалы про ботов:
# 1. Всё, о чём должен знать разработчик Телеграм-ботов
#    https://itnan.ru/post.php?c=1&p=543676
# 2. Как написать telegram-бота на python с помощью библиотеки telebot
#    https://bookflow.ru/kak-napisat-telegram-bota-na-python-s-pomoshhyu-biblioteki-telebot/
# 3. Кнопки в телеграм-ботах
#    https://vc.ru/u/1185570-mihail-gok/462161-knopki-v-telegram-botah
# Создание кнопок для телеграмм бота с использованием библиотеки pyTelegramBotAPI:
# https://habr.com/ru/sandbox/163347/
#
# https://docs-python.ru/packages/biblioteka-python-telegram-bot-python/menju-klaviatury/

# Как делать команды в стартовом меню:
# 4. Инструкция: Как создавать ботов в Telegram
#    https://habr.com/ru/post/262247/
"""
help - Справка по всем командам бота
url - Переход на сайт, с которого собираются статьи
parse - Выводит в чат заголовки и ссылки статей
parse_to_file - Отправляет в чат файл, содержащий заголовки и ссылки статей
choice_inline - Выбор из нескольких пунктов с использованием InlineKeyboardMarkup
choice_reply - Выбор из нескольких пунктов с использованием ReplyKeyboardMarkup
string - В зависимости от параметров выводит текст большими, маленькими буквами или с первой буквой заглавной
formatted_text - примеры форматирования текста в сообщениях
sticker - Отправляет фиксированный стикер в чат
pics - Отправляет одну из двух картинок в чат
"""

from lesson20_parser import parser, parser_to_file

if __name__ == '__main__':
    TOKEN = 'тут должен быть токен - который удалил, чтобы не показывать'

    bot = telebot.TeleBot(TOKEN)


    def split_command_string(message, par=False):
        """
        Разбирает входящий текст на компоненты.
        :param message: Сообщение из телеграм.
        :param par: Требуется выделять параметр или нет.
        :return: mes_text - это или список из двух строк, или строка
        """
        mes_lst = message.text.split()
        mes_command = mes_lst[0]
        mes_text = ' '.join(mes_lst[1:])
        if par and len(mes_lst) >= 3:
            mes_text = [mes_lst[1],
                        ' '.join(mes_lst[2:])]
        return mes_command, mes_text


    def split_parse_string(message):
        mes_lst = message.text.split()
        mes_command = mes_lst[0]
        # Возможные варианты при правильном формировании параметров в строке message
        # mes_lst[0] - Команда.
        # mes_lst[1] - Если преобразуется в положительное целое, то количество статей.
        #              Если ошибка при преобразовании - то первое слово в запросе.
        # mes_lst[2:] - Параметры запроса.
        #
        # То есть, такие варианты могут быть:
        # Вариант 1: mes_lst[1] преобразуется в положительное целое
        #     mes_command = mes_lst[0]
        #     mes_num = mes_lst[1]
        #     mes_query = mes_lst[2]+mes_lst[3]+mes_lst[4]...
        # Вариант 2: mes_lst[1] даёт ошибку при преобразовании в положительное целое
        #     mes_command = mes_lst[0]
        #     mes_num = None
        #     mes_query = mes_lst[1]+mes_lst[2]+mes_lst[3]+mes_lst[4]...
        if len(mes_lst) == 1:
            # Только команда
            num_correct = False
            mes_num = None
            mes_query = ''
            return mes_command, mes_num, mes_query, num_correct
        elif len(mes_lst) == 2:
            # Команда и один параметр.
            # Трактуем его как количество статей.
            mes_query = ''
        else:
            # команда и два параметра
            mes_query = '+'.join(mes_lst[2:])

        num_correct = True
        mes_num = mes_lst[1]

        try:
            mes_num = int(mes_num)  # Целое
            if mes_num <= 0:  # Целое, больше нуля
                mes_query = '+'.join(mes_lst[1:])
        except ValueError:
            num = None
            num_correct = False
            mes_query = '+'.join(mes_lst[1:])

        return mes_command, mes_num, mes_query, num_correct


    @bot.message_handler(commands=['parse'])
    def send_command_parse(message):
        chat_id = message.chat.id
        mes_command, mes_num, mes_query, num_correct = split_parse_string(message)

        bot.reply_to(message, f'Тестовый вывод.\nКоманда {mes_command}\n' +
                     f'num: {mes_num}\nquery: {mes_query}\n')
        if num_correct:
            _, references = parser(max_news_num=mes_num, query=mes_query)
        else:
            _, references = parser(query=mes_query)

        if len(references) == 0:
            # Список пуст
            bot.send_message(chat_id, f'По запросу статьи отсутствуют.\nЗапрос на поиск:\n{mes_query}')
        else:
            for ref in references:
                bot.send_message(chat_id, f'{ref[0]} - {ref[1]}')


    @bot.message_handler(commands=['parse_to_file'])
    def send_command_parse(message):
        chat_id = message.chat.id
        mes_command, mes_num, mes_query, num_correct = split_parse_string(message)

        bot.reply_to(message, f'Тестовый вывод.\nКоманда {mes_command}\n' +
                     f'num: {mes_num}\nquery: {mes_query}\n')
        if num_correct:
            parser_to_file(max_news_num=mes_num, query=mes_query)
        else:
            parser_to_file(query=mes_query)

        if exists('data.json'):
            with open('data.json', encoding='utf-8') as f:
                bot.send_document(chat_id, f)
        else:
            bot.send_message(chat_id,
                             'Произошла ошибка - файл не сформирован. ' +
                             'Попробуйте повторить команду /parse_to_file ' +
                             'с теми же параметрами')


    @bot.message_handler(commands=['start'])
    def send_command_start(message):
        mes_command, mes_text = split_command_string(message)
        bot.reply_to(message, f'Команда {mes_command}')


    @bot.message_handler(commands=['choice_reply'])
    def send_command_choice_reply(message):
        mes_command, mes_text = split_command_string(message)
        # bot.reply_to(message, f'Команда {mes_command}')
        # создаём клавиатуру
        markup_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                    one_time_keyboard=True)
        # У объекта обычной клавиатуры есть ещё две полезных опции:
        # one_time_keyboard для скрытия кнопок после нажатия и
        # selective для показа клавиатуры лишь некоторым участникам группы.

        # Создав клавиатуру, создадим к ней кнопки
        # button1 = types.KeyboardButton(text='Привет')
        # markup_keyboard.add(button1)
        # button2 = types.KeyboardButton(text='Пока')
        # markup_keyboard.add(button2)
        # Метод add() при каждом вызове создаёт новую строку (ряд) и
        # принимает произвольное число аргументов по количеству
        # желаемых кнопок в строке.
        buttons = ['Привет', 'Пока']
        markup_keyboard.add(*buttons)
        # btn1 = types.KeyboardButton("Привет")
        # btn2 = types.KeyboardButton("Пока")
        # markup.add(btn1, btn2)
        markup_keyboard.add('Это кнопка одна на всю строку')

        # Можно так:
        # markup_keyboard.row('Привет', 'Пока')
        # markup_keyboard.row('Это кнопка одна на всю строку')
        bot.send_message(message.chat.id,
                         f'Команда {mes_command}',
                         reply_markup=markup_keyboard)
        # Чтобы удалить кнопки, необходимо отправить новое сообщение
        # со специальной «удаляющей» клавиатурой типа ReplyKeyboardRemove


    @bot.message_handler(commands=['choice_inline'])
    def send_command_choice_inline(message):
        # mes_command, mes_text = split_command_string(message)
        # bot.reply_to(message, f'Команда {mes_command}')

        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup_keyboard = types.InlineKeyboardMarkup()
        itembtna = types.InlineKeyboardButton(text='aaaaaaaaaaa types.InlineKeyboardButton 123456778901234567890',
                                              callback_data='Button_a')
        itembtnb = types.InlineKeyboardButton(text='b', callback_data='Button_b')
        itembtnv = types.InlineKeyboardButton(text='v', callback_data='Button_v')
        itembtnc = types.InlineKeyboardButton(text='c', callback_data='Button_c')
        itembtnd = types.InlineKeyboardButton(text='d', callback_data='Button_d')
        itembtne = types.InlineKeyboardButton(text='e', callback_data='Button_e')
        markup_keyboard.row(itembtna)
        markup_keyboard.row(itembtnb)
        markup_keyboard.row(itembtnv, itembtnc, itembtnd, itembtne)
        # markup.add(itembtna, itembtnb, itembtnv, itembtnc, itembtnd, itembtne)
        bot.send_message(message.chat.id, "Выберите букву:", reply_markup=markup_keyboard)


    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        print('call:', call)
        # markup = types.editMessageReplyMarkup(selective=False)
        # bot.send_message(call.message.chat.id, "callback_query_handler")
        # bot.send_message(call.message.chat.id, f"Data: {str(call.data)}", reply_markup=markup)
        bot.send_message(call.message.chat.id, f"Выбрали кнопку: {str(call.data)}")

        # удаляем инлайновую клаву
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Тут было сообщение с выбором кнопок",
                              reply_markup=None)

        # # Если сообщение из чата с ботом
        # if call.message:
        #     if call.data == "test":
        #         bot.edit_message_text(chat_id=call.message.chat.id,
        #                               message_id=call.message.message_id,
        #                               text="Пыщь")
        #         bot.send_message(call.message.chat.id, text="Пыщь")
        # # Если сообщение из инлайн-режима
        # elif call.inline_message_id:
        #     if call.data == "test":
        #         # bot.edit_message_text(inline_message_id=call.inline_message_id,
        #         #                       text="Бдыщь")
        #         bot.send_message(call.message.chat.id, text="Бдыщь")
        # bot.send_message(call.message.chat.id, 'Data: {}'.format(str(call.data)))
        # bot.answer_callback_query(call.id)


    @bot.message_handler(commands=['url'])
    def send_command_url(message):
        mes_command, mes_text = split_command_string(message)
        # bot.reply_to(message, f'Команда {mes_command}')

        chat_id = message.chat.id
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Сайт Python Дайджест - новости о python на определенную тему",
                                             url='https://pythondigest.ru')
        markup.add(button1)
        bot.send_message(message.chat.id,
                         f"Привет, <u>{message.from_user.first_name}</u>! Нажми на кнопку и перейди на сайт)",
                         parse_mode='HTML',
                         reply_markup=markup)


    @bot.message_handler(commands=['string'])
    def send_command_upper(message):
        mes_command, mes_text = split_command_string(message, par=True)
        if isinstance(mes_text, list):
            if mes_text[0].lower() == 'upper':
                reply_text = (f'Команда {mes_command}.\nПараметр {mes_text[0]}.\n\n' +
                              f'Текст заглавными буквами:\n{mes_text[1].upper()}')
            elif mes_text[0].lower() == 'lower':
                reply_text = (f'Команда {mes_command}.\nПараметр {mes_text[0]}.\n\n' +
                              f'Текст маленькими буквами:\n{mes_text[1].lower()}')
            else:
                reply_text = (f'Команда {mes_command}.\nДопустимые параметры отсутствуют.\n\n' +
                              f'Текст с первой заглавной буквой:\n{" ".join(mes_text).capitalize()}')
        else:
            reply_text = (f'Команда {mes_command}.\nДопустимые параметры отсутствуют.\n\n' +
                          f'Текст с первой заглавной буквой:\n{mes_text.capitalize()}')
        bot.reply_to(message, reply_text)


    @bot.message_handler(commands=['help'])
    def send_command_help(message):
        help_txt = ('<b><i>Список команд:</i></b>\n' +
                    '\n' +
                    '/help – Выводит этот текст.\n' +
                    '/start – Ничего не делает, но отвечает.\n' +
                    '\n' +
                    '/url – Переход на сайт https://pythondigest.ru, с которого ' +
                    'собираются статьи.\n' +
                    '/parse [articles_num] {query} – Выводит в чат заголовки и ' +
                    'ссылки статей с сайта https://pythondigest.ru для указанного ' +
                    'в параметре articles_num количества статей, удовлетворяющих ' +
                    'запросу {query}. Вывод производится по статье в сообщении.\n' +
                    '/parse_to_file [articles_num] {query} – Отправляет в чат файл, ' +
                    'содержащий заголовки и ссылки статей с сайта https://pythondigest.ru ' +
                    'для указанного в параметре articles_num количества статей, ' +
                    'удовлетворяющих запросу {query}.\n' +
                    '\n' +
                    '<i>Пример</i> (для команды /parse_to_file - аналогично):\n' +
                    ' – Отправляет в чат до 5 статей, удовлетворяющих поиску "flask" и "django":' +
                    '<pre>     /parse 5 flask django</pre>\n' +
                    ' – Отправляет в чат все найденные статьи, удовлетворяющих поиску "FastAPI":' +
                    '<pre>     /parse FastAPI</pre>\n' +
                    '\n' +
                    '/choice_inline – Выбор из нескольких пунктов с использованием ' +
                    'InlineKeyboardMarkup.\n' +
                    '/choice_reply – Выбор из нескольких пунктов с использованием ' +
                    'ReplyKeyboardMarkup\n' +
                    '\n' +
                    '/string [upper | lower] text – В зависимости от параметров выводит ' +
                    'текст большими / маленькими буквами или с первой буквой заглавной\n' +
                    '<i>Пример</i>:\n' +
                    ' – Выводит текст "ТЕКСТ_ДЛЯ_ОБРАБОТКИ" большими буквами:' +
                    '<pre>     /string upper текст_для_обработки</pre>\n' +
                    ' – Выводит текст "текст_для_обработки" маленькими буквами:' +
                    '<pre>     /string lower ТЕКСТ_ДЛЯ_ОБРАБОТКИ</pre>\n' +
                    ' – Выводит текст "Текст_для_обработки" с первой заглавной буквой:' +
                    '<pre>     /string текст_для_обработки</pre>\n' +
                    '\n' +
                    '/formatted_text – примеры форматирования текста в сообщениях.\n' +
                    '/sticker – Отправляет фиксированный стикер в чат.\n' +
                    '/pics – Отправляет одну из двух картинок в чат.\n' +
                    '\n' +
                    '<b><i>Действия:</i></b>\n' +
                    'При получении сообщения со стикером – в ответ отправляется ' +
                    'стикер по умолчанию.\n' +
                    'При получении сообщения с текстом – в ответ отправляется ' +
                    'сообщение, содержащее ' +
                    'исходный текст и перевёрнутый текст.')
        # bot.reply_to(message, help_txt, parse_mode=ParseMode.HTML)
        # bot.reply_to(message, help_txt, parse_mode='HTML')
        bot.send_message(message.chat.id, help_txt, parse_mode='HTML')


    @bot.message_handler(commands=['formatted_text'])
    def send_command_formatted_text(message):
        text = ('В этом сообщении пример форматированного текста.\n' +
                '\n' +
                'Ссылка на документацию (они же пример явно указанных ссылок): ' +
                '<a href="https://core.telegram.org/bots/api#sendmessage">Метод sendMessage</a> и ' +
                '<a href="https://core.telegram.org/bots/api#formatting-options">Formatting options</a>\n' +
                'Ссылка на профиль пользователя телеграм: ' +
                '<a href="tg://user?id=1467499466">Разработчик бота shilyas_ru_test</a>\n' +
                # Статья: Бот Telegram: как упомянуть пользователя по его идентификатору (а не по имени пользователя)
                # https://question-it.com/questions/11683736/bot-telegram-kak-upomjanut-polzovatelja-po-ego-identifikatoru-a-ne-po-imeni-polzovatelja?ysclid=l9e5z28rs3719428479
                #  Эти упоминания гарантированно сработают только в том случае, если пользователь
                #  связывался с ботом в прошлом, отправил запрос обратного вызова боту с помощью
                #  встроенной кнопки или является участником группы, в которой он был упомянут.
                #  Другая проблема с этим методом заключается в том, что он будет уведомлять
                #  пользователя, даже если вы установите disable_notification.
                #  Не работает, если пользователь отключил «Переадресованные сообщения»
                #  в настройках конфиденциальности.
                '\n' +
                '<u>Подчёркнутый текст.</u>\n' +  # Синоним: <ins>underline</ins>
                '<b>Жирный текст.</b>\n' +  # Синоним: <strong>bold</strong>
                '<i>Текст курсивом.</i>\n' +  # Синоним: <em>italic</em>
                'Текст <b>жирным <i>курсивом.</i></b>\n' +
                '<s>Зачеркнутый текст.</s>\n' +  # Синоним: <strike>strikethrough</strike>, <del>strikethrough</del>
                '<s>Зачеркнутый текст <b>жирным <i>курсивом.</i></b></s>\n' +
                '\n' +
                'Спойлер (скрытый текст) - активируйте касанием:\n' +
                '<tg-spoiler><i>Тут находится скрытый текст, написанный курсивом.</i></tg-spoiler>\n' +
                '\n' +
                '<code>Отображение одной или нескольких строк текста, ' +
                'который представляет собой программный код.\n' +
                'Это элемент (тэг) &lt;code&gt; в HTML.</code>\n' +
                '\n' +
                '<pre>    Блок предварительно ' +
                'форматированного       текста.\n' +
                'Это элемент (тэг) &lt;pre&gt; в HTML.</pre>\n' +
                '\n' +
                'Тэги &lt;pre&gt; и &lt;code&gt; могут быть вложенными.')
        bot.send_message(message.chat.id,
                         text,
                         parse_mode='HTML')


    @bot.message_handler(commands=['sticker'])
    def send_command_sticker(message):
        FILE_ID = 'CAACAgIAAxkBAAMfY008-3exhTK87wdC08JzY06aqU0AAvMFAAKW-hIFglF0nnoQERQqBA'
        bot.send_sticker(message.chat.id, FILE_ID)


    @bot.message_handler(commands=['pics'])
    def send_command_sticker(message):
        pics_file_name = 'pic1-165693.jpg' if random() < 0.5 else 'pic2-1384729.jpg'
        with open(pics_file_name, 'rb') as data:
            bot.send_photo(message.chat.id, data)


    @bot.message_handler(content_types=['sticker'])
    def send_sticker(message):
        # print(message)
        FILE_ID = 'CAADAgADPQMAAsSraAsqUO_V6idDdBYE'
        bot.send_sticker(message.chat.id, FILE_ID)


    @bot.message_handler(content_types=['text'])
    def reverse_text(message):
        chat_id = message.chat.id
        text = message.text
        markup_keyboard_remove = types.ReplyKeyboardRemove()
        # Чтобы удалить кнопки, необходимо отправить новое сообщение
        # со специальной «удаляющей» клавиатурой типа ReplyKeyboardRemove
        print('text:', message)
        if (text == 'Привет' or
                text == 'Пока' or
                text == 'Это кнопка одна на всю строку'):
            bot.send_message(chat_id,
                             f'Выбрали кнопку с текстом: {text}',
                             reply_markup=markup_keyboard_remove)
        else:
            bot.reply_to(message,
                         f'Набран текст:\n{text}\n\nПеревёрнутый текст:\n{text[::-1]}',
                         reply_markup=markup_keyboard_remove)


    bot.polling()
