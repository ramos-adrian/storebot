from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler

from library import my_filters
from library.utils import message


def handler():
    hd = CommandHandler("controlpanel", run, my_filters.is_registered)
    return hd


@message
def run(u, c, _):
    _.reply(_.l("opening_menu"), reply_markup=markup(_.l))
    return


# Do not delete this function. Because it is used in languages.py
def markup(l):
    return l("languages")+"|"+l("chatflows")
