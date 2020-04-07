from telegram.ext import MessageHandler, Filters

from objects.User import User


def handler():
    hd = MessageHandler(Filters.all, update)
    return hd


def update(u, c):
    tg_user = u.effective_user
    user = User(tg_user)
    user.register()
    return
