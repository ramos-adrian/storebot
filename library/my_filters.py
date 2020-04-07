import os

from telegram.ext import BaseFilter

import settings
from objects.User import User


class owner(BaseFilter):
    """
    This is a cumstom filter class to be used with a MessageHandler object.
    """

    def __init__(self):
        return

    def filter(self, message):
        flag = False
        user_id = message.from_user.id
        owner_id = os.environ['OWNER_ID'].split(",")
        if str(user_id) in owner_id:
            flag = True
        return flag


class is_registered(BaseFilter):
    """
    This is a cumstom filter class to be used with a MessageHandler object.
    """

    def __init__(self):
        return

    def filter(self, message):
        tg_id = message.from_user
        user = User(tg_id)
        return user.is_registered()


class user_lang_text(BaseFilter):
    """
    This is a cumstom filter class to be used with a MessageHandler object.
    """

    def __init__(self, text):
        self.text = text
        return

    def filter(self, message):
        tg_id = message.from_user
        user = User(tg_id)
        if message.text:
            text = message.text
        elif message.caption:
            text = message.caption
        else:
            text = ""
        lang = settings.lang.get(user.language_code_in_bot)
        if not lang:
            lang = settings.lang["default"]
        original = lang.get(self.text)
        if original == text:
            return True
        return False


owner = owner()
is_registered = is_registered()
