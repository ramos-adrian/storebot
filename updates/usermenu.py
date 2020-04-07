from telegram.ext import CommandHandler

from library import my_filters
from library.utils import message


def handler():
    hd = CommandHandler("menu", run, my_filters.is_registered)
    return hd


@message
def run(u, c, _):
    _.reply(_.l("opening_menu"), reply_markup=markup(_.l))
    return


def markup(l):
    return l("language")
