import ephem
import logging

import cities
import settings

from datetime import datetime as dt
from random import choice
from string import punctuation
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

API_KEY = settings.API_KEY
DATE_TODAY = dt.today().strftime("%Y/%m/%d")
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO,
                    filename="bot.log")

CITIES = cities.ru_cities


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


def get_letter(word, position='last'):
    if word is None:
        return None
    else:
        word = word.lower()
        if position == 'first':
            letter = word[0]
        else:
            letter = word[-1] if word[-1] not in 'йьы' else word[-2]
        return letter


def prettify_name(name):
    if not name:
        return
    if ' ' in name:
        p_name = ' '.join([x.capitalize() for x in name.split()])
    elif '-' in name:
        p_name = '-'.join([x.capitalize() for x in name.split('-') if len(x) > 2])
    else:
        p_name = name.capitalize()
    return p_name


def cities_game_logic(user_city, bot_city_prev, remaining_cities):
    notice = None
    bot_city = None
    last_letter_prev = get_letter(bot_city_prev)
    first_letter = get_letter(user_city, position='first')
    if bot_city_prev is None or (first_letter == last_letter_prev):
        user_city = user_city.lower()
        if user_city in remaining_cities.get(first_letter, (None,)):
            remaining_cities[first_letter].remove(user_city)
            last_letter = get_letter(user_city)
            bot_city = choice(list(remaining_cities.get(last_letter)))
            remaining_cities[last_letter].remove(bot_city)
        else:
            user_city = prettify_name(user_city)
            notice = f"Город с названием '{user_city}' уже называли, либо его не существует в России."
    else:
        notice = f"Введите название российского города на букву '{last_letter_prev}'."
    return bot_city, remaining_cities, notice


def cities_game(update, context):
    if not context.args:
        response = "Ваш ход."
    else:
        user_city = ' '.join(context.args)
        bot_city, remaining_cities, notice = cities_game_logic(user_city,
                                                               context.user_data.get('bot_city_prev'),
                                                               context.user_data.get('remaining_cities', CITIES))
        context.user_data['bot_city_prev'] = bot_city
        context.user_data['remaining_cities'] = remaining_cities
        bot_city = prettify_name(bot_city)
        response = notice if notice is not None else f"{bot_city}, Ваш ход."
    update.message.reply_text(response)


def main():
    bot = Updater(API_KEY)

    dp = bot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", get_constelation))
    dp.add_handler(CommandHandler("next_full_moon", get_next_full_moon))
    dp.add_handler((CommandHandler("wordcount", wordcount)))
    dp.add_handler((CommandHandler("cities", cities_game)))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    main()
