import logging
import os
from io import BytesIO

import telegram.bot
import yaml
from telegram import TelegramError, File, Document
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request

import settings
from library import Ranks, ConfigurationLib
from objects import dbmanager, ChatflowBuilder
from updates import messages, controlpanel, languages, usermenu, setlanguage, chatflows, popupmenu, start


def load_configuration():
    """
    Load the configuration and language file.
    """
    load_languages()
    create_ranks()
    return


def load_languages():
    lang_conf = ConfigurationLib.read_configuration_file("library/lang_default.yml")
    settings.lang["default"] = lang_conf
    for code, file_id in get_languages():
        with BytesIO() as file:
            Document(file_id, bot=bot).get_file().download(out=file)
            settings.lang[code] = yaml.full_load(file.getvalue().decode("utf-8"))
    return


def get_languages():
    conn, c = dbmanager.get_connection()
    query = "SELECT * FROM languages"
    c.execute(query)
    results = c.fetchall()
    c.close()
    conn.close()
    _languages = []
    for result in results:
        _result = result["code"], result["file_id"]
        _languages.append(_result)
    return _languages


def load_chatflows():
    for cf_id, name, file_id in chatflows.get_chatflows():
        chatflows.setup_chatflow(name, file_id, bot)
    return


def create_ranks():
    Ranks.add_rank("user", 10000)
    Ranks.add_rank("staff", 50000)
    # Ranks.add_rank_permission("staff", "cmd.broadcast", 1)
    return


class MQBot(telegram.bot.Bot):
    """A subclass of Bot which delegates send method handling to MQ"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        msg = None
        try:
            msg = super(MQBot, self).send_message(*args, **kwargs)
        except TelegramError as error:
            print(error)
        return msg

    @mq.queuedmessage
    def forward_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        msg = None
        try:
            msg = super(MQBot, self).forward_message(*args, **kwargs)
        except TelegramError as error:
            print(error)
        return msg

    @mq.queuedmessage
    def send_photo(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        msg = None
        try:
            msg = super(MQBot, self).send_photo(*args, **kwargs)
        except TelegramError as error:
            print(error)
        return msg


def add_events():
    def add_msg():
        refresh_user_data = messages.handler()
        settings.user_menu_popup_handler = refresh_user_data
        dsp.add_handler(refresh_user_data, 2)
        dsp.add_handler(start.handler())
        return

    def add_cmd():
        dsp.add_handler(controlpanel.handler())
        dsp.add_handler(usermenu.handler())
        return

    def add_conv():
        dsp.add_handler(languages.handler())
        dsp.add_handler(setlanguage.handler())
        dsp.add_handler(chatflows.handler())
        dsp.add_handler(languages.replace_handler())
        dsp.add_handler(chatflows.replace_handler())
        return

    def add_callback_query():
        dsp.add_handler(languages.delete_handler())
        dsp.add_handler(chatflows.delete_handler())
        return

    def add_popup_menu():
        popup_menu_handlers = popupmenu.handlers()
        settings.popup_menu_handlers = popup_menu_handlers
        for handler in popup_menu_handlers:
            dsp.add_handler(handler)
        return

    dsp = upd.dispatcher
    add_conv()
    add_cmd()
    add_msg()
    add_callback_query()
    #add_popup_menu()  # Popup menu must be at then end to not block other events
    return


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
token = os.environ.get('TOKEN')
q = mq.MessageQueue(all_burst_limit=29, all_time_limit_ms=1000)
request = Request(con_pool_size=8)
bot = MQBot(token, request=request, mqueue=q)
upd = telegram.ext.updater.Updater(bot=bot, use_context=True)
settings.dispatcher = upd.dispatcher
settings.job_queue = upd.job_queue

Ranks.create_db_tables()
dbmanager.create_tables()
dbmanager.initialize_database()
load_configuration()
add_events()
# Load chatflows needs to be separated function because it needs to be after the default events are loaded.
load_chatflows()

mode = os.getenv('MODE', 'polling')

if mode == "polling":
    upd.start_polling()
    print("Starting polling...")
elif mode == "heroku":
    APP_NAME = os.environ.get("APP_NAME")
    if APP_NAME:
        PORT = int(os.environ.get('PORT', '8443'))
        upd.start_webhook(listen="0.0.0.0", port=PORT, url_path=token)
        upd.bot.set_webhook("https://" + APP_NAME + ".herokuapp.com/" + token)
        upd.idle()
    else:
        print("Enviroment variable APP_NAME not defined")
else:
    print("Enviroment variable MODE not defined.")
