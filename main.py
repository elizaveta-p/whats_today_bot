import io

from pprint import pprint

from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import datetime
from api_key import TOKEN
from features.making_picture import make_picture, image_to_bytes
from features.getting_holidays import get_list_of_countries, get_holidays, country_codes, create_country_codes_dict, make_readable
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
    get_list_of_countries()


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
    # print(holiday)

    keyboard = [[InlineKeyboardButton(text=x[0], callback_data=x[0])] for x in holiday]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    update.message.reply_text(make_readable(holiday, date), reply_markup=markup)


def choose_holiday(update, context):
    query = update.callback_query
    # query.answer()
    choice = query.data
    print(choice)
    byte_im = create_picture(choice)
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
    main()
