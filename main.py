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


# reply_keyboard = [['/address', '/phone'],
#                   ['/site', '/work_time']]
# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def echo(update, context):
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    update.message.reply_text(f"Я получил сообщение: {update.message.text}")


def start(update, context):
    update.message.reply_text("Привет! Я......")
    get_list_of_countries()
#
#
# def help(update, context):
#     update.message.reply_text(
#         "Я пока не умею помогать... Я только ваше эхо.")


def time(update, context):
    update.message.reply_text(str(datetime.datetime.now().time()))


# def date(update, message):
#     update.message.reply_text(str(datetime.datetime.now().date()))


def image(update, context):
    # filename = 'data/images/image.jpg'
    # with open(filename, 'rb') as file:
    #     update.message.reply_photo(file)
    im = make_picture()
    byte_im = image_to_bytes(im)
    update.message.reply_photo(byte_im)


def holidays(update, context):
    update.message.reply_text('Загружаю праздники...')
    date = datetime.datetime.now().date()
    # print(date)
    if context.args and context.args[0] != 'all':
        # print(context.args)
        country = context.args
        holiday = get_holidays(date, country)
    elif context.args[0] == 'all':
        # get_list_of_countries()
        country = [country_codes[x] for x in country_codes.keys()]
        holiday = get_holidays(date, country)
    else:
        holiday = get_holidays(date)
    # print(holiday)

    keyboard = [[InlineKeyboardButton(text=x[0], callback_data=x[0])] for x in holiday]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard, )

    update.message.reply_text(make_readable(holiday, date), reply_markup=markup)


def choose_holiday(update, context):

    print(update)
    # chat_id = update.message.chat_id
    query = update.callback_query
    chat_id = query.message.chat.id
    print(chat_id)
    # query.answer()

    # This will define which button the user tapped on (from what you assigned to "callback_data". As I assigned them "1" and "2"):
    choice = query.data
    print(choice)
    # print(update is None)
    byte_im = create_picture(choice)
    # print(update is None)
    context.bot.send_photo(chat_id,
                           byte_im)
    # update.message.reply_photo(byte_im)

    # Now u can define what choice ("callback_data") do what like this:
    # if choose == '1':
    #     func1()
    #
    # if choose == '2':
    #     func2()


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
    dp.add_handler(CommandHandler("time", time))
    # dp.add_handler(CommandHandler("date", date))
    dp.add_handler(CommandHandler("image", image))
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
