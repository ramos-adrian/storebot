from telegram.ext import MessageHandler

from library import my_filters
from updates import controlpanel, usermenu


def handlers():
    _handlers = []
    hd_owner = MessageHandler(my_filters.owner, controlpanel.run)
    hd_user = MessageHandler(my_filters.is_registered, usermenu.run)
    _handlers.append(hd_owner)
    _handlers.append(hd_user)
    return _handlers


def get_replymarkup(user, l):
    if user.is_owner():
        return controlpanel.markup(l)
    else:
        return usermenu.markup(l)
