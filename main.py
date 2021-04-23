# -*- coding: utf-8 -*-
import io

import pytz
from dateutil.tz import tzutc, tzlocal

from pprint import pprint

from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import datetime
from api_key import TOKEN
from features.making_picture import make_picture, image_to_bytes
from features.getting_holidays import get_list_of_countries, get_holidays, make_readable
from features.wiki_search import search_in_wiki
from translator.translator import translate
from translator.decode_url import decode_cyrillic_urls
import datetime
from data.exceptions.errors import PastDateError, FutureDateError


# reply_keyboard = [['/address', '/phone'],
#                   ['/site', '/work_time']]
# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def echo(update, context):
    update.message.reply_text(f"Я получил сообщение: {update.message.text}")


def start(update, context):
    update.message.reply_text("Привет! Я......")


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def notify_me(update, context):
    chat_id = update.message.chat_id
    try:
        if context.args:
            time = datetime.datetime.strptime(context.args[0], "%H:%M").time()
        else:
            time = datetime.datetime.strptime('00:00', "%H:%M").time()

        job_removed = remove_job_if_exists(
            str(chat_id),
            context
        )
        local_timezone = pytz.timezone('Europe/Moscow')
        target_time = datetime.time(hour=time.hour, minute=time.minute).replace(tzinfo=local_timezone)
        # print(target_time)
        context.job_queue.run_daily(
            callback=send_holidays,
            context=chat_id,
            days=(0, 1, 2, 3, 4, 5, 6),
            time=target_time,
            name=str(chat_id))
        text = f'Оповещения будут приходить в {time:%H:%M} каждый день.'
        if job_removed:
            text += ' Старая задача удалена.'
        # Присылаем сообщение о том, что всё получилось.
        update.message.reply_text(text)
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')


def dont_notify_me(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Оповещения больше приходить не будут.' if job_removed else 'Оповещения не были установлены.'
    update.message.reply_text(text)


def send_holidays(context):
    job = context.job
    date = datetime.date.today()
    # print(f"here at time {datetime.datetime.now().time()}")
    # chat_id = context.message.chat_id
    # job = context.job
    # pprint(job)
    holiday = get_holidays(date)
    print(holiday)
    # my_str = [f"{x[1][0]} в {x[1][1]}" for x in enumerate(holiday)]
    keyboard = [[InlineKeyboardButton(text=str(x[0] + 1), callback_data=x[1]['en']) for x in enumerate(holiday)]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # context.message.reply_text(text=make_readable(holiday, date), reply_markup=markup)
    # context.bot.send_message(chat_id=job.context, text=make_readable(holiday, date), reply_markup=markup)
    context.bot.send_message(job.context, text=make_readable(holiday, date), reply_markup=markup)

    # update.message.reply_text(make_readable(holiday, date), reply_markup=markup)


def holidays(update, context):
    print(context)
    update.message.reply_text('Загружаю праздники...')
    if context.args:
        date = datetime.datetime.strptime(context.args[0], '%d-%m-%Y').date()  # ValueError если не подходит под формат
        if date < datetime.date.today():
            raise PastDateError
        elif date.year > 2025:
            raise FutureDateError
    else:
        date = datetime.date.today()

    # print(date)
    holiday = get_holidays(date)
    print(holiday)
    keyboard = [[InlineKeyboardButton(text=x["name"], callback_data=x['en'])] for x in holiday]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    update.message.reply_text(make_readable(holiday, date), reply_markup=markup)


def choose_holiday(update, context):
    query = update.callback_query
    choice = translate(query.data)
    print(choice)
    wiki_result = search_in_wiki(choice)
    if wiki_result["completed"]:
        new_url = decode_cyrillic_urls(wiki_result['url'])
        caption = '\n\n'.join(["Результат поиска в Википедии:", wiki_result["title"],
                               wiki_result["body"], new_url])
    else:
        caption = choice
    holiday_name = choice.split(' в ')[0]
    byte_im = create_picture(holiday_name)
    context.bot.send_photo(query.message.chat.id, photo=byte_im)
    context.bot.send_message(text=caption, chat_id=query.message.chat.id)


def create_picture(text):
    im = make_picture(text)
    byte_image = image_to_bytes(im)
    return byte_image


def countries(update, context):
    if context.args:
        num = int(context.args[0])
    else:
        num = None
    country = get_list_of_countries(num)
    # print(country)
    update.message.reply_text(country)


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN, use_context=True)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    # Создаём обработчик сообщений типа Filters.text
    # из описанной выше функции echo()
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(Filters.text, echo)
    updater.dispatcher.add_handler(CallbackQueryHandler(choose_holiday))

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("countries", countries))
    dp.add_handler(CommandHandler("holidays", holidays))
    dp.add_handler(CommandHandler("notify_me", notify_me,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("dont_notify_me", dont_notify_me,
                                  pass_chat_data=True))

    dp.add_handler(text_handler)

    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    # get_list_of_countries()
    main()
