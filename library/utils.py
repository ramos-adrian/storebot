import functools

import emoji
import validators
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler

import settings
from objects.User import User


def message(func):
    """
    Decorator to provide functions shortcuts.
    """

    # To get functions shortcut:
    # Receive "functions" argument in your decorated function
    @functools.wraps(func)
    def wrapper(update, context):
        def _language(key, **kwargs):
            """
            Return a language string.
            :param key:
            :param kwargs: Arguments for str.format() method.
            :return:
            """
            lang_code = User(update.effective_user).language_code_in_bot
            lang = settings.lang.get(lang_code)
            if not lang:
                lang = settings.lang["default"]
            text = lang.get(key, settings.lang["default"].get(key, "ERROR: MISSING STRING!")).format(**kwargs)
            text = emoji.emojize(text, use_aliases=True)
            return text

        def _reply(text, *args, reply_markup=None, **kwargs):
            if type(reply_markup) == str:
                if reply_markup.startswith("inline."):
                    reply_markup = build_inlinekeyboard(reply_markup)
                else:
                    reply_markup = build_replykeyboard(reply_markup)
            return update.message.reply_html(text, *args, reply_markup=reply_markup, **kwargs)

        def _reply_document(*args, reply_markup=None, **kwargs):
            if type(reply_markup) == str:
                if reply_markup.startswith("inline."):
                    reply_markup = build_inlinekeyboard(reply_markup)
                else:
                    reply_markup = build_replykeyboard(reply_markup)
            return update.message.reply_document(*args, reply_markup=reply_markup, **kwargs)

        class functions:
            def reply(*args, reply_markup=None, **kwargs):
                return _reply(*args, reply_markup=reply_markup, **kwargs)

            def reply_document(*args, reply_markup=None, **kwargs):
                return _reply_document(*args, reply_markup=reply_markup, **kwargs)

            def l(*args, **kwargs):
                return _language(*args, **kwargs)

            user = User(update.effective_user)
            text = update.message.text

        result = func(update, context, functions)
        return result

    return wrapper


def build_replykeyboard(string):
    """
    Build a replymarkup keyboard from a string.
    :param string:
    :return:
    """
    rows = string.split("||")
    keyboard = []
    for row in rows:
        _row = []
        buttons = row.split("|")
        for button in buttons:
            btn = KeyboardButton(button)
            _row.append(btn)
        keyboard.append(_row)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    return reply_markup


def build_inlinekeyboard(string):
    """
    Build a inline keyboard from a string.
    :param string:
    :return:
    """
    string = string[7:]
    rows = string.split("||")
    keyboard = []
    for row in rows:
        _row = []
        buttons = row.split("|")
        for button in buttons:
            text, data = button.split("::")
            if not validators.url(data):
                btn = InlineKeyboardButton(text=text, callback_data=data)
            else:
                btn = InlineKeyboardButton(text=text, url=data)
            _row.append(btn)
        keyboard.append(_row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def callbackquery(func):
    """
    Decorator to provide functions shortcuts.
    """

    # To get functions shortcut:
    # Receive "functions" argument in your decorated function
    @functools.wraps(func)
    def wrapper(update, context):
        def _language(key, **kwargs):
            """
            Return a language string.
            :param key:
            :param kwargs: Arguments for str.format() method.
            :return:
            """
            lang_code = User(update.effective_user).language_code_in_bot
            lang = settings.lang.get(lang_code)
            if not lang:
                lang = settings.lang["default"]
            text = lang.get(key, settings.lang["default"].get(key, "ERROR: MISSING STRING!")).format(**kwargs)
            return text

        def _reply(text, *args, reply_markup=None, **kwargs):
            if type(reply_markup) == str:
                reply_markup = build_replykeyboard(reply_markup)

            return update.callback_query.message.reply_html(text, *args, reply_markup=reply_markup, **kwargs)

        class functions:
            def reply(*args, reply_markup=None, **kwargs):
                return _reply(*args, reply_markup=reply_markup, **kwargs)

            def l(*args, **kwargs):
                return _language(*args, **kwargs)

            user = User(update.effective_user)
            data = update.callback_query.data
            msg = update.callback_query.message

        result = func(update, context, functions)
        return result

    return wrapper


@message
def cancel(u, c, _):
    _.reply(_.l("cancel_action"))
    return ConversationHandler.END


cancel_cmd_hd = CommandHandler("cancel", cancel)
