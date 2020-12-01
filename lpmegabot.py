import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import date
from string import punctuation
import ephem
import settings

logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO,
                    filename="bot.log")

API_KEY = settings.API_KEY
DATE_TODAY = date.today().strftime("%Y/%m/%d")


def greet_user(update, context):
    text = "Вызван /start"
    update.message.reply_text(text)


def talk_to_me(update, context):
    user_text = update.message.text
    update.message.reply_text(user_text)


def get_constelation(update, context):
    user_text = update.message.text
    _, planet = user_text.split()
    planet = planet.lower().capitalize()
    try:
        p = getattr(ephem, planet)(DATE_TODAY)
    except AttributeError:
        update.message.reply_text("I don't know this planet. Maybe you meant the Moon?")
        planet = "Moon"
        p = getattr(ephem, planet)(DATE_TODAY)
    try:
        _, constellation = ephem.constellation(p)
        update.message.reply_text(f"Today {planet.capitalize()} is in the constellation of {constellation}.")
    except TypeError:
        update.message.reply_text("It's not a planet. Enter the name of a planet in the Solar System.")


def wordcount(update, context):
    _, *words = update.message.text.split()
    text = ' '.join(words)
    for char in punctuation:
        text = text.replace(char, '')
    n_words = len(text.split())
    spec_cases = {0: "No word.", 1: "1 word."}
    result = spec_cases.get(n_words, f"{n_words} words.")

    update.message.reply_text(result)


def main():
    bot = Updater(API_KEY)

    dp = bot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", get_constelation))
    dp.add_handler((CommandHandler("wordcount", wordcount)))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    main()
