from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters as F, ConversationHandler, CommandHandler

from library import utils, Ranks
from library.utils import message
from library.my_filters import user_lang_text as ftext
from objects import dbmanager
from updates import usermenu, start
from updates.languages import get_languages

RECEIVE_LANGUAGE = 1


def handler():
    # started filter indicate that the user has already selected a language when started the bot
    filters = ~Ranks.permission("started")
    start_cmd = CommandHandler("start", asklanguage, filters)
    entry_hd = MessageHandler(F.private & F.text & ftext("language"), asklanguage)
    entry_points = [entry_hd, start_cmd]
    receive_language_hd = MessageHandler(F.text, receive_language)
    states = {
        RECEIVE_LANGUAGE: [receive_language_hd]
    }
    fallbacks = [utils.cancel_cmd_hd]
    hd = ConversationHandler(entry_points=entry_points, states=states, fallbacks=fallbacks)
    return hd


@message
def asklanguage(u, c, _):
    _.reply(_.l("select_language"), reply_markup=kb(_.l))
    return RECEIVE_LANGUAGE


def kb(l):
    languages = get_languages()
    keyboard = []
    for _, name, _ in languages:
        if len(keyboard) == 0 or len(row) == 3:
            row = list()
            if len(keyboard) == 0:
                row.append(l("default_language_name"))
            keyboard.append(row)
        row.append(name)
    if len(languages) == 0:
        keyboard.append([l("default_language_name")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    return reply_markup


WELCOME_STICKER = "CAACAgEAAxkBAAIUZ16LtVL_jrNcg48-rDe2w9rjw5MnAAJNAAMDTvQhsPzBh868lXYYBA"


@message
def receive_language(u, c, _):
    name = _.text
    lang_code = get_language_code(name, _.l)
    if not lang_code:
        text = _.l("invalid_language") + "\n" + _.l("select_language")
        _.reply(text, reply_markup=kb(_.l))
        return RECEIVE_LANGUAGE
    if lang_code == "dft":
        _.user.language_code_in_bot = None
    else:
        _.user.language_code_in_bot = lang_code
    if _.user.has_permission("started"):
        _.reply(_.l("settings_saved"))
    else:
        _.user.add_permission("started")
        start.start(u, c)
    return ConversationHandler.END


def get_language_code(name, l):
    if name == l("default_language_name"):
        return "dft"
    conn, c = dbmanager.get_connection()
    c.execute("SELECT code FROM languages WHERE name = %s", (name,))
    result = c.fetchone()
    c.close()
    conn.close()
    if result:
        return result["code"]
    return False
