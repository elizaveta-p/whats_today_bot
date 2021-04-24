import pytz
import logging
import telegram.error
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# from api_key import TOKEN
import config.TOKEN
from features.making_picture import make_picture, image_to_bytes
from features.getting_holidays import get_list_of_countries, get_holidays, make_readable
from features.wiki_search import search_in_wiki
from translator.translator import translate
from translator.decode_url import decode_cyrillic_urls
import datetime
from data.exceptions.errors import PastDateError, FutureDateError

logging.basicConfig(
    filename='data/my_log.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


def unknown_text(update, context):
    update.message.reply_text(f'Не удалось распознать сообщение "{update.message.text}", для справки нажмите /help')


def start(update, context):
    update.message.reply_text("Привет! Я бот, для получения сведений о праздниках и создания онлайн-открыток с ними. Помощь - /help")


def help(update, context):
    data = open('data/help.txt', 'r', encoding='utf-8').read()
    update.message.reply_text(data)


def remove_job_if_exists(name, context):
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
        logging.info(f'notifications added at {target_time}')
        context.job_queue.run_daily(
            callback=send_holidays,
            context=chat_id,
            days=(0, 1, 2, 3, 4, 5, 6),
            time=target_time,
            name=str(chat_id))
        text = f'Оповещения будут приходить в {time:%H:%M} каждый день.'
        if job_removed:
            text += ' Старая задача удалена.'
        update.message.reply_text(text)
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /notify_me чч:мм')
    except telegram.error.TelegramError as te:
        logging.warning(te)


def dont_notify_me(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Оповещения больше приходить не будут.' if job_removed else 'Оповещения не были установлены.'
    update.message.reply_text(text)


def send_holidays(context):
    job = context.job
    date = datetime.date.today()
    holiday = get_holidays(date)
    keyboard = [[InlineKeyboardButton(text=str(x[0] + 1), callback_data=x[1]['en']) for x in enumerate(holiday)]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    context.bot.send_message(job.context, text=make_readable(holiday, date), reply_markup=markup)


def holidays(update, context):
    try:
        if context.args:
            date = datetime.datetime.strptime(context.args[0], '%d-%m-%Y').date()  # ValueError если не подходит под формат
            if date < datetime.date.today():
                raise PastDateError
            elif date.year > 2025:
                raise FutureDateError
        else:
            date = datetime.date.today()
        update.message.reply_text('Загружаю праздники...')
        holiday = get_holidays(date)
        keyboard = [[InlineKeyboardButton(text=x["name"], callback_data=x['en'])] for x in holiday]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        update.message.reply_text(make_readable(holiday, date), reply_markup=markup)
    except PastDateError or FutureDateError:
        update.message.reply_text("Поддерживаются только праздники настоящего и будущего")
    except ValueError:
        update.message.reply_text("Использование: /holidays [дд-мм-гггг]")


def choose_holiday(update, context):
    try:
        logging.info('making info about holiday')
        query = update.callback_query
        choice = translate(query.data)
        logging.info('connecting to wiki')
        wiki_result = search_in_wiki(choice)
        logging.info(f'wiki found: {wiki_result["completed"]}')
        if wiki_result["completed"]:
            new_url = decode_cyrillic_urls(wiki_result['url'])
            logging.info('cyrillic url decoded')
            caption = '\n\n'.join(["Результат поиска в Википедии:", wiki_result["title"],
                                   wiki_result["body"], new_url])
        else:
            caption = choice
        holiday_name = choice.split(' в ')[0]
        byte_im = create_picture(holiday_name)
        context.bot.send_photo(query.message.chat.id, photo=byte_im)
        context.bot.send_message(text=caption, chat_id=query.message.chat.id)
    except BaseException as be:
        logging.error(be)


def create_picture(text):
    try:
        logging.info('creating picture')
        im = make_picture(text)
        logging.info('converting to bytes')
        byte_image = image_to_bytes(im)
        return byte_image
    except BaseException as be:
        logging.error(be)


def countries(update, context):
    try:
        if context.args:
            num = int(context.args[0])
        else:
            num = None
        logging.info(f'getting list of countries, num: {num}')
        country = get_list_of_countries(num)
        update.message.reply_text(country)
    except KeyError as ke:
        logging.warning(ke)
    except telegram.error.TelegramError as e:
        logging.warning(e)


def main():
    try:
        updater = Updater(config.TOKEN, use_context=True)
        dp = updater.dispatcher
        text_handler = MessageHandler(Filters.text, unknown_text)
        updater.dispatcher.add_handler(CallbackQueryHandler(choose_holiday))

        dp.add_handler(CommandHandler("help", help))
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
        updater.start_polling()
        updater.idle()
    except telegram.error.TelegramError as e:
        logging.fatal(e)
    except BaseException as e:
        logging.fatal(e)


if __name__ == '__main__':
    main()
