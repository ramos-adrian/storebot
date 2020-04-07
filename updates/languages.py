import os
from io import BytesIO, StringIO

import yaml
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler, CallbackQueryHandler

import settings
from library import ConfigurationLib, utils
from library.my_filters import user_lang_text as text
from library.my_filters import owner
from library.utils import message, callbackquery, cancel_cmd_hd
from objects import dbmanager
from updates import controlpanel

RECEIVE_OPTION = 1
RECEIVE_NEW_NAME = 2
RECEIVE_NEW_CODE = 3
RECEIVE_NEW_FILE = 4
REPLACE_RECEIVE_FILE = 5


def handler():
    entry_txt_hd = MessageHandler(owner & text("languages"), show_menu)
    entry_points = [entry_txt_hd]
    show_languages_hd = MessageHandler(owner & text("my_languages"), show_languages)
    new_language_hd = MessageHandler(owner & text("new_language"), new_language)
    receive_new_name_hd = MessageHandler(owner & ~Filters.command, receive_new_name)
    receive_new_code_hd = MessageHandler(owner & ~Filters.command, receive_new_code)
    receive_new_file_hd = MessageHandler(owner & Filters.document, receive_new_file)
    states = {
        RECEIVE_OPTION: [show_languages_hd, new_language_hd],
        RECEIVE_NEW_NAME: [receive_new_name_hd],
        RECEIVE_NEW_CODE: [receive_new_code_hd],
        RECEIVE_NEW_FILE: [receive_new_file_hd]
    }
    fallbacks = [cancel_cmd_hd]
    conv = ConversationHandler(states=states, entry_points=entry_points, fallbacks=fallbacks)
    return conv


@message
def show_menu(u, c, _):
    kb = _.l("my_languages") + "|" + _.l("new_language")
    _.reply(_.l("select_option"), reply_markup=kb)
    return RECEIVE_OPTION


@message
def show_languages(u, c, _):
    for code, name, file_id in get_languages():
        caption = _.l("language_name") + name + "\n" + _.l("language_code") + code
        del_data = "deletelanguage_" + code
        replace_data = "replacelanguage_" + code
        kb = "inline." + _.l("delete") + "::" + del_data + "||" + _.l("replace") + "::" + replace_data
        _.reply_document(document=file_id, file_name=name, caption=caption, reply_markup=kb)
    _.reply(_.l("select_option"), reply_markup=controlpanel.kb(_.l))
    return ConversationHandler.END


def get_languages():
    languages = []
    conn, c = dbmanager.get_connection()
    c.execute("SELECT * FROM languages")
    results = c.fetchall()
    c.close()
    conn.close()
    for result in results:
        languages.append((result["code"], result["name"], result["file_id"]))
    return languages


@message
def new_language(u, c, _):
    _.reply(_.l("insert_new_language_name"), reply_markup=ReplyKeyboardRemove())
    return RECEIVE_NEW_NAME


@message
def receive_new_name(u, c, _):
    name = u.message.text
    if language_exists(name):
        _.reply(_.l("language_name_already_exists") + "\n" + _.l("insert_new_language_name"))
        return RECEIVE_NEW_NAME
    c.user_data["new_language_name"] = name
    _.reply(_.l("insert_new_language_code"))
    return RECEIVE_NEW_CODE


def language_exists(name):
    if name == "dft":
        return True
    conn, c = dbmanager.get_connection()
    c.execute("SELECT id FROM languages WHERE name = %s OR code = %s", (name, name))
    result = c.fetchone()
    c.close()
    conn.close()
    if result:
        return True
    return False


@message
def receive_new_code(u, c, _):
    code = u.message.text
    if language_exists(code):
        _.reply(_.l("language_code_already_exists") + "\n" + _.l("insert_new_language_code"))
        return RECEIVE_NEW_CODE
    c.user_data["new_language_code"] = code.lower()
    with open("library/lang_default.yml", "rb") as file:
        u.message.reply_document(document=file, caption=_.l("default_file"))
    return RECEIVE_NEW_FILE


#TODO Use objects in memory
@message
def receive_new_file(u, c, _):
    file_id = u.message.document.file_id
    add_language(c.user_data["new_language_name"], c.user_data["new_language_code"], file_id)
    path = "library/" + file_id
    u.message.document.get_file().download(path)
    settings.lang[c.user_data["new_language_code"]] = ConfigurationLib.read_configuration_file(path)
    os.remove(path)
    _.reply(_.l("language_added"))
    return ConversationHandler.END


def add_language(name, code, file_id):
    conn, c = dbmanager.get_connection()
    c.execute("INSERT INTO languages(name, code, file_id) VALUES(%s, %s, %s) ON CONFLICT(name) DO "
              "UPDATE SET file_id = %s", (name, code, file_id, file_id))
    conn.commit()
    c.close()
    conn.close()
    return


def delete_handler():
    hd = CallbackQueryHandler(delete_language, pattern="^(deletelanguage_)")
    return hd


@callbackquery
def delete_language(u, c, _):
    if not _.user.is_owner():
        return
    lang_code = _.data.split("_")[1]
    file_id = delete_language_from_db(lang_code)
    set_default_language_in_users(lang_code)
    try:
        del settings.lang[lang_code]
    except Exception:
        pass
    _.msg.delete()
    _.msg.reply_document(caption=_.l("language_deleted"), document=file_id)
    return


def set_default_language_in_users(lang_code):
    conn, c = dbmanager.get_connection()
    c.execute("UPDATE users SET language_code_in_bot = Null WHERE language_code_in_bot = %s", (lang_code,))
    conn.commit()
    c.close()
    conn.close()
    return


def delete_language_from_db(code):
    conn, c = dbmanager.get_connection()
    c.execute("SELECT file_id FROM languages WHERE code = %s", (code,))
    result = c.fetchone()
    if result:
        result = result["file_id"]
    c.execute("DELETE FROM languages WHERE code = %s", (code,))
    conn.commit()
    c.close()
    conn.close()
    return result


def replace_handler():
    entry_callback = CallbackQueryHandler(replace_ask_file, pattern="^(replacelanguage_)")
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
    language_code = u.callback_query.data.split("_")[1]
    language = get_language_from_code(language_code)
    c.user_data["replace_language"] = language
    txt = _.l("send_replacing_language", name=language["name"])
    _.reply(txt, reply_markup=ReplyKeyboardRemove())
    return REPLACE_RECEIVE_FILE


@message
def receive_file_fallback(u, c, _):
    chatflow_name = c.user_data["replace_language"]["name"]
    txt = _.l("send_replacing_language", name=chatflow_name)
    u.message.reply_html(txt)
    return REPLACE_RECEIVE_FILE


@message
def receive_file(u, c, _):
    document = u.message.document
    code = c.user_data["replace_language"]["code"]
    with BytesIO() as file:
        document.get_file().download(out=file)
        _file = file.getvalue()
        lang_name = c.user_data["replace_language"]["name"]
        lang_code = c.user_data["replace_language"]["code"]
        add_language(lang_name, lang_code, document.file_id)
        settings.lang[code] = yaml.full_load(_file)
    u.message.reply_html(_.l("language_updated"))
    return ConversationHandler.END


def get_language_from_code(language_code):
    conn, c = dbmanager.get_connection()
    query = "SELECT * FROM languages WHERE code = %s"
    c.execute(query, (language_code,))
    result = c.fetchone()
    c.close()
    conn.close()
    if result:
        return result
    else:
        return
