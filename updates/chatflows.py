import json
from io import BytesIO

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, Document
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

import settings
from library.my_filters import owner
from library.my_filters import user_lang_text as text
from library.utils import cancel_cmd_hd, message, callbackquery
from objects import dbmanager, ChatflowBuilder
from updates import controlpanel

RECEIVE_OPTION = 1
RECEIVE_NEW_NAME = 2
RECEIVE_NEW_FILE = 3
REPLACE_RECEIVE_FILE = 4


def handler():
    entry_txt_hd = MessageHandler(owner & text("chatflows"), show_menu)
    entry_points = [entry_txt_hd]
    show_chatflows_hd = MessageHandler(owner & text("my_chatflows"), show_chatflows)
    new_chatflow_hd = MessageHandler(owner & text("new_chatflow"), new_chatflow)
    receive_new_name_hd = MessageHandler(owner & ~Filters.command, receive_new_name)
    receive_new_file_hd = MessageHandler(owner & Filters.document, receive_new_file)
    states = {
        RECEIVE_OPTION: [show_chatflows_hd, new_chatflow_hd],
        RECEIVE_NEW_NAME: [receive_new_name_hd],
        RECEIVE_NEW_FILE: [receive_new_file_hd]
    }
    fallbacks = [cancel_cmd_hd]
    conv = ConversationHandler(states=states, entry_points=entry_points, fallbacks=fallbacks)
    return conv


@message
def show_menu(u, c, _):
    kb = _.l("my_chatflows") + "||" + _.l("new_chatflow")
    _.reply(_.l("select_option"), reply_markup=kb)
    return RECEIVE_OPTION


@message
def show_chatflows(u, c, _):
    for cf_id, name, file_id in get_chatflows():
        caption = _.l("chatflow_name") + str(name)
        del_data = "deletechatflow_" + str(cf_id)
        replace_data = "replacechatflow_" + str(cf_id)
        kb = "inline."+_.l("delete")+"::" + del_data + "||"+_.l("replace")+"::" + replace_data
        _.reply_document(document=file_id, file_name=name, caption=caption, reply_markup=kb)
    _.reply(_.l("select_option"), reply_markup=controlpanel.kb(_.l))
    return ConversationHandler.END


def get_chatflows():
    chatflows = []
    conn, c = dbmanager.get_connection()
    c.execute("SELECT * FROM chatflows")
    results = c.fetchall()
    c.close()
    conn.close()
    for result in results:
        chatflows.append((result["id"], result["name"], result["file_id"]))
    return chatflows


@message
def new_chatflow(u, c, _):
    _.reply(_.l("insert_new_chatflow_name"), reply_markup=ReplyKeyboardRemove())
    return RECEIVE_NEW_NAME


@message
def receive_new_name(u, c, _):
    name = u.message.text
    if chatflow_exists(name):
        _.reply(_.l("chatflow_name_already_exists") + "\n" + _.l("insert_new_chatflow_name"))
        return RECEIVE_NEW_NAME
    c.user_data["new_chatflow_name"] = name
    _.reply(_.l("insert_new_chatflow_file"))
    return RECEIVE_NEW_FILE


def chatflow_exists(name):
    conn, c = dbmanager.get_connection()
    c.execute("SELECT id FROM chatflows WHERE name = %s", (name,))
    result = c.fetchone()
    c.close()
    conn.close()
    if result:
        return True
    return False


@message
def receive_new_file(u, c, _):
    document = u.message.document
    with BytesIO() as file:
        document.get_file().download(out=file)
        my_json = json.loads(file.getvalue().decode('utf-8-sig'))
        verify, error = ChatflowBuilder.verify_integrity(my_json)
        if not verify:
            _.reply(_.l("invalid_chatflow"), error)
            return ConversationHandler.END
    chatflow_name = c.user_data["new_chatflow_name"]
    setup_chatflow(chatflow_name, document.file_id, c.bot)
    _.reply(_.l("chatflow_added"))
    return ConversationHandler.END


def get_dict_chatflow(file_id, bot):
    with BytesIO() as file:
        Document(file_id, file_unique_id=0, bot=bot).get_file().download(out=file)
        string = file.getvalue().decode('utf-8-sig')
        json_chatflow = json.loads(string)
    return json_chatflow


def setup_chatflow(name, file_id, bot):
    add_chatflow_to_db(name, file_id)
    json_chatflow = get_dict_chatflow(file_id, bot)
    conv_handler = ChatflowBuilder.build(json_chatflow)
    settings.registered_chatflows[name] = conv_handler
    dsp = settings.dispatcher
    dsp.remove_handler(settings.user_menu_popup_handler)
    dsp.add_handler(conv_handler)
    dsp.add_handler(settings.user_menu_popup_handler)
    return


def add_chatflow_to_db(name, file_id):
    conn, c = dbmanager.get_connection()
    data = (name, file_id, file_id)
    c.execute("INSERT INTO chatflows(name, file_id) VALUES(%s, %s) ON CONFLICT(name) DO UPDATE SET file_id = %s", data)
    conn.commit()
    c.close()
    conn.close()
    return


def delete_handler():
    hd = CallbackQueryHandler(delete_chatflow, pattern="^(deletechatflow_)")
    return hd


@callbackquery
def delete_chatflow(u, c, _):
    if not _.user.is_owner():
        return
    chatflow_id = _.data.split("_")[1]
    name, file_id = delete_chatflow_from_db(chatflow_id)
    settings.dispatcher.remove_handler(settings.registered_chatflows[name])
    try:
        del settings.registered_chatflows[name]
    except Exception:
        pass
    _.msg.delete()
    _.msg.reply_document(caption=_.l("chatflow_deleted"), document=file_id)
    return


def delete_chatflow_from_db(chatflow_id):
    conn, c = dbmanager.get_connection()
    c.execute("SELECT name, file_id FROM chatflows WHERE id = %s", (chatflow_id,))
    result = c.fetchone()
    if result:
        result = result["name"], result["file_id"]
    c.execute("DELETE FROM chatflows WHERE id = %s", (chatflow_id,))
    conn.commit()
    c.close()
    conn.close()
    return result


def replace_handler():
    entry_callback = CallbackQueryHandler(replace_ask_file, pattern="^(replacechatflow_)")
    entry_points = [entry_callback]
    receive_file_hd = MessageHandler(Filters.document, receive_file)
    receive_file_fallback_hd = MessageHandler(~Filters.document & ~Filters.command, receive_file_fallback)
    states = {
        REPLACE_RECEIVE_FILE: [receive_file_hd, receive_file_fallback_hd]
    }
    fallbacks = [cancel_cmd_hd]
    conv = ConversationHandler(entry_points=entry_points, states=states, fallbacks=fallbacks)
    return conv


@callbackquery
def replace_ask_file(u, c, _):
    u.callback_query.answer()
    chatflow_id = u.callback_query.data.split("_")[1]
    chatflow = get_chatflow_from_id(chatflow_id)
    c.user_data["replace_chatflow"] = chatflow
    txt = _.l("send_replacing_chatflow", name=chatflow["name"])
    u.callback_query.message.reply_html(txt, reply_markup=ReplyKeyboardRemove())
    return REPLACE_RECEIVE_FILE


@message
def receive_file_fallback(u, c, _):
    chatflow_name = c.user_data["replace_chatflow"]["name"]
    txt = _.l("send_replacing_chatflow", name=chatflow_name)
    u.message.reply_html(txt)
    return REPLACE_RECEIVE_FILE


@message
def receive_file(u, c, _):
    document = u.message.document
    chatflow_name = c.user_data["replace_chatflow"]["name"]
    with BytesIO() as file:
        document.get_file().download(out=file)
        _file = file.getvalue().decode('utf-8-sig')
        my_json = json.loads(_file)
        verify, error = ChatflowBuilder.verify_integrity(my_json)
        if not verify:
            _.reply(_.l("invalid_chatflow", error=error))
            return ConversationHandler.END
    settings.dispatcher.remove_handler(settings.registered_chatflows[chatflow_name])
    setup_chatflow(chatflow_name, document.file_id, c.bot)
    u.message.reply_html(_.l("chatflow_updated"))
    return ConversationHandler.END


def get_chatflow_from_id(chatflow_id):
    conn, c = dbmanager.get_connection()
    query = "SELECT * FROM chatflows WHERE id = %s"
    c.execute(query, (chatflow_id,))
    result = c.fetchone()
    c.close()
    conn.close()
    if result:
        return result
    else:
        return
