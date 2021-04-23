import io

from pprint import pprint

from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import datetime
from api_key import TOKEN
from features.making_picture import make_picture, image_to_bytes
from features.getting_holidays import get_list_of_countries, get_holidays, make_readable
from translator.translator import translate
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

# def remove_job_if_exists(name, context):
#     """Удаляем задачу по имени.
#     Возвращаем True если задача была успешно удалена."""
#     current_jobs = context.job_queue.get_jobs_by_name(name)
#     if not current_jobs:
#         return False
#     for job in current_jobs:
#         job.schedule_removal()
#     return True


# Обычный обработчик, как и те, которыми мы пользовались раньше.
# def set_timer(update, context):
#     """Добавляем задачу в очередь"""
#     pass
#
#
# def notify_me(update, context):
#     chat_id = update.message.chat_id
#     try:
#         # args[0] должен содержать значение аргумента
#         # (секунды таймера)
#         time = int(context.args[0])
#         if due < 0:
#             update.message.reply_text(
#                 'Извините, не умеем возвращаться в прошлое')
#             return
#
#         # Добавляем задачу в очередь
#         # и останавливаем предыдущую (если она была)
#         job_removed = remove_job_if_exists(
#             str(chat_id),
#             context
#         )
#         context.job_queue.run_once(
#             task,
#             due,
#             context=chat_id,
#             name=str(chat_id)
#         )
#         text = f'Вернусь через {due} секунд!'
#         if job_removed:
#             text += ' Старая задача удалена.'
#         # Присылаем сообщение о том, что всё получилось.
#         update.message.reply_text(text)
#
#     except (IndexError, ValueError):
#         update.message.reply_text('Использование: /set <секунд>')


def holidays(update, context):
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
    # my_str = [f"{x[1][0]} в {x[1][1]}" for x in enumerate(holiday)]
    keyboard = [[InlineKeyboardButton(text=str(x[0] + 1), callback_data=x[1]['en']) for x in enumerate(holiday)]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    update.message.reply_text(make_readable(holiday, date), reply_markup=markup)


def choose_holiday(update, context):
    query = update.callback_query
    # query.answer()
    choice = translate(query.data)
    holiday_name = choice.split(' в ')[0]
    print(choice)
    byte_im = create_picture(holiday_name)
    context.bot.send_photo(query.message.chat.id, photo=byte_im, caption=choice)


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
    print(country)
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
