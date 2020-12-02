import ephem
import logging
import settings

from datetime import datetime as dt
from string import punctuation
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


API_KEY = settings.API_KEY
DATE_TODAY = dt.today().strftime("%Y/%m/%d")
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO,
                    filename="bot.log")


def greet_user(update, context):
    text = "Вызван /start"
    update.message.reply_text(text)


def talk_to_me(update, context):
    text = update.message.text
    update.message.reply_text(text)


def get_constelation(update, context):
    *_, planet = context.args
    planet = planet.lower().capitalize()
    try:
        p = getattr(ephem, planet)(DATE_TODAY)
    except AttributeError:
        update.message.reply_text("I don't know this planet. Maybe you meant the Moon?")
        planet = "Moon"
        p = getattr(ephem, planet)(DATE_TODAY)
    try:
        *_, constellation = ephem.constellation(p)
        update.message.reply_text(f"Today {planet.capitalize()} is in the constellation of {constellation}.")
    except TypeError:
        update.message.reply_text("It's not a planet. Enter the name of a planet in the Solar System.")


def wordcount(update, context):
    text = ' '.join(context.args)
    for char in punctuation:
        text = text.replace(char, '')
    n_words = len(text.split())
    spec_cases = {0: "No word.", 1: "1 word."}
    result = spec_cases.get(n_words, f"{n_words} words.")

    update.message.reply_text(result)


def get_next_full_moon(update, context):
    text = update.message.text
    _, user_date = text.split()
    try:
        norm_date = dt.strptime(user_date, '%Y-%m-%d')
    except ValueError:
        norm_date = DATE_TODAY
        update.message.reply_text("Enter the date in the format 'YYYY-MM-DD'.\n"
                                  "Next full moon relative to today:")

    result = ephem.next_full_moon(norm_date)
    update.message.reply_text(result)


def main():
    bot = Updater(API_KEY)

    dp = bot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", get_constelation))
    dp.add_handler(CommandHandler("next_full_moon", get_next_full_moon))
    dp.add_handler((CommandHandler("wordcount", wordcount)))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    main()
