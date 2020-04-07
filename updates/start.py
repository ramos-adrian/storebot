from telegram.ext import CommandHandler, Filters

import settings
from library import Ranks
from library.utils import message
from updates import usermenu

WELCOME_STICKER = "CAACAgEAAxkBAAIUZ16LtVL_jrNcg48-rDe2w9rjw5MnAAJNAAMDTvQhsPzBh868lXYYBA"


def handler():
    filters = Filters.private & Ranks.permission("started")
    hd = CommandHandler("start", start, filters)
    return hd


@message
def start(u, c, _):
    msg = _.reply(_.l("welcome_1", name=u.effective_user.first_name), queued=False)
    c.user_data["welcome_msg_blink"] = 0
    c.user_data["welcome_name"] = u.effective_user.first_name
    c.user_data["state_eye"] = "open"
    settings.job_queue.run_repeating(edit_welcome, interval=4, first=2, context=(msg, _.l, c.user_data))
    u.message.reply_sticker(sticker=WELCOME_STICKER)
    usermenu.run(u, c)
    return


def edit_welcome(c):
    job = c.job
    msg, l, user_data = c.job.context
    name = user_data["welcome_name"]
    state_eye = user_data["state_eye"]
    if state_eye == "open":
        msg.edit_text(text=l("welcome_2", name=name))
        user_data["state_eye"] = "closed"
    else:
        msg.edit_text(text=l("welcome_1", name=name))
        user_data["state_eye"] = "open"
    if user_data["welcome_msg_blink"] > 5:
        job.schedule_removal()
    user_data["welcome_msg_blink"] += 1
    return
