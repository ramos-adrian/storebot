import re

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import MessageHandler, CallbackQueryHandler, ConversationHandler, Filters

from objects.User import User
from updates import usermenu


def verify_integrity(json_file):
    """
    :return: (boolean, string): True if file is valid, otherwhise False
    """
    flag, error = verify_entry(json_file)
    if not flag:
        return flag, error
    flag, error = verify_steps(json_file)
    if not flag:
        return flag, error
    return True, "ok"


def verify_entry(json_file):
    entry = json_file.get("entry")
    if not entry:
        return False, "Entry not found."
    for _object in entry:
        if not _object.get("text"):
            return False, "Entry object does not have an 'text' field."
        if not _object.get("goto"):
            return False, "Entry object does not have an 'goto' field"
    return True, "ok"


def verify_steps(json_file):
    for item in json_file.values():
        for message in item:
            text = message.get("text")
            photo = message.get("photo")
            if (not text) and (not photo):
                return False, "Step has neither 'text' nor 'photo' field."
            keyboard = message.get("keyboard")
            inline_keyboard = message.get("inline_keyboard")
            if keyboard:
                if type(keyboard) != list:
                    return False, "Keyboard is not a list."
                for row in keyboard:
                    if type(row) != list:
                        return False, "Keyboard is not a list of lists."
                    for button in row:
                        btn_text = button.get("text")
                        btn_goto = button.get("goto")
                        if not btn_text:
                            return False, "Button in keyboard has no 'text' field."
                        if not btn_goto:
                            return False, "Button in keyboard has no 'goto' field."
            elif inline_keyboard:
                if type(inline_keyboard) != list:
                    return False, "Inline keyboard is not a list."
                for row in inline_keyboard:
                    if type(row) != list:
                        return False, "Inline keyboard is not a list of lists."
                    for button in row:
                        btn_text = button.get("text")
                        btn_edit_text = button.get("edit_text")
                        btn_link = button.get("link")
                        if not btn_text:
                            return False, "Button in inline keyboard has no 'text' field."
                        if not btn_edit_text and not btn_link:
                            return False, "Button in inline keyboard has neither 'edit_text' nor 'link' field."
    return True, "ok"


def build(json_chatflow):
    entry_points = build_entry_points(json_chatflow)
    fallbacks = []
    states = build_states(json_chatflow, fallbacks)
    fallbacks.append(MessageHandler(Filters.all, showmenu))
    conversation = ConversationHandler(entry_points=entry_points, states=states, fallbacks=fallbacks)
    return conversation


def showmenu(u, c):
    usermenu.run(u, c)
    return ConversationHandler.END


def build_entry_points(json_chatflow):
    entry_points = []
    entry_list = json_chatflow["entry"]
    for entry in entry_list:
        text = str(entry["text"])
        goto = entry["goto"]
        function = function_builder("entry", chatflow=json_chatflow, goto_step=goto, update_type="message")
        function_callbackquery = function_builder("entry", chatflow=json_chatflow, goto_step=goto,
                                                  update_type="callback")
        msg_hd = MessageHandler(Filters.regex(re.escape(text)), function)
        callbackquery_handler = CallbackQueryHandler(function_callbackquery, pattern=re.escape(text))
        entry_points.extend([msg_hd, callbackquery_handler])
    return entry_points


def build_states(json_chatflow, fallbacks):
    states = {}
    for key, state in json_chatflow.items():
        if key == "entry":
            continue
        states[key] = []
        for message in state:
            keyboard = message.get("keyboard")
            inline_keyboard = message.get("inline_keyboard")
            if (not keyboard) and (not inline_keyboard):
                continue
            if keyboard:
                for button in get_keyboard_buttons(keyboard):
                    create_states_handler(json_chatflow, fallbacks, states, key, button["text"], quickreply=button)
            elif inline_keyboard:
                for button in get_inline_keyboard_buttons(inline_keyboard):
                    create_states_handler(json_chatflow, fallbacks, states, key, button["text"], edit_button=button)

    return states


def create_states_handler(json_chatflow, fallbacks, states, key, text, goto_step=None, quickreply=None, edit_button=None):
    callbackquery_function = None
    function = None

    if not goto_step:
        callbackquery_function = function_builder("edit", chatflow=json_chatflow, goto_step=goto_step,
                                                  update_type="callback", edit_button=edit_button)
    else:
        function = function_builder("state", chatflow=json_chatflow, goto_step=goto_step, update_type="message")
        callbackquery_function = function_builder("state", chatflow=json_chatflow, quickreply=quickreply,
                                                  update_type="callback", edit_button=edit_button)

    if function:
        handler = MessageHandler(Filters.regex(re.escape(text)), function)
        states[key].append(handler)
    if callbackquery_function:
        callbackquery_handler = CallbackQueryHandler(callbackquery_function, pattern=re.escape(text))
        states[key].append(callbackquery_handler)
        fallbacks.append(callbackquery_handler)
    return


def get_keyboard_buttons(keyboard):
    buttons = []
    for row in keyboard:
        for button in row:
            buttons.append(button)
    return buttons


def get_inline_keyboard_buttons(keyboard):
    buttons = []
    for row in keyboard:
        for button in row:
            if button.get("edit_text"):
                buttons.append(button)
    return buttons


def function_builder(function_type, chatflow=None, goto_step=None, update_type=None, quickreply=None, edit_button=None):
    """
    :param quickreply:
    :param edit_button: (Option) To be used with inline_buttons that have edit_text field
    represents the new text that will replace the current message text.
    :param function_type:  Can be 'entry' or 'state'
    :param goto_step: Used for entry
    :param chatflow:
    :param update_type: Can be 'message' or 'callback' it defines from where the message object is taken.
    :return:
    """

    def state_function(u, c):

        message = get_message(u)

        _goto_step = quickreply["goto"]
        # messages contains messages to be sent in this step
        messages = chatflow[_goto_step]
        for step_message in messages:
            text = step_message.get("text")
            photo = step_message.get("photo")
            tag = quickreply.get("tag")
            if tag:
                user = User(u.effective_user)
                user.addtag(tag)
            disable_web_page_preview = step_message.get("disable_web_page_preview")
            reply_markup = get_reply_markup(step_message)
            if photo:
                message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup)
            else:
                message.reply_html(text=text, reply_markup=reply_markup,
                                   disable_web_page_preview=disable_web_page_preview)

        return _goto_step

    def entry_function(u, c):

        message = get_message(u)

        # messages contains messages to be sent in this step
        messages = chatflow[goto_step]
        for step_message in messages:
            text = step_message.get("text")
            photo = step_message.get("photo")
            tag = step_message.get("tag")
            if tag:
                user = User(u.effective_user)
                user.addtag(tag)
            disable_web_page_preview = step_message.get("disable_web_page_preview")
            reply_markup = get_reply_markup(step_message)
            if photo:
                message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup)
            else:
                message.reply_html(text=text, reply_markup=reply_markup,
                                   disable_web_page_preview=disable_web_page_preview)

        return goto_step

    def state_edit_function(u, c):
        u.callback_query.answer()
        message = get_message(u)
        reply_markup = message.reply_markup
        text = edit_button.get("text")
        tag = edit_button.get("tag")
        if tag:
            user = User(u.effective_user)
            user.addtag(tag)
        disable_web_page_preview = edit_button.get("disable_web_page_preview")
        if message.text:
            message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
        elif message.caption:
            message.edit_caption(text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
        return None

    def get_message(u):
        if update_type == "message":
            return u.message
        else:
            return u.callback_query.message

    if function_type == 'entry':
        return entry_function
    elif function_type == 'state':
        return state_function
    elif function_type == 'edit':
        return state_edit_function
    return


def get_reply_markup(message):
    keyboard = message.get("keyboard")
    inline_keyboard = message.get("inline_keyboard")
    remove_keyboard = message.get("remove_keyboard")
    if keyboard:
        reply_markup = get_markup_keyboard(keyboard)
    elif inline_keyboard:
        reply_markup = get_markup_inline_keyboard(inline_keyboard)
    elif remove_keyboard:
        reply_markup = ReplyKeyboardRemove()
    else:
        reply_markup = None
    return reply_markup


def get_markup_keyboard(keyboard):
    rows = []
    for row in keyboard:
        _row = []
        for button in row:
            text = button["text"]
            _row.append(text)
        rows.append(_row)
    reply_markup = ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)
    return reply_markup


def get_markup_inline_keyboard(keyboard):
    rows = []
    for row in keyboard:
        _row = []
        for button in row:
            text = button["text"]
            edit_text = button.get("edit_text")
            link = button.get("link")
            inline_button = None
            if edit_text:
                inline_button = InlineKeyboardButton(text=text, callback_data=text)
            elif link:
                inline_button = InlineKeyboardButton(text=text, url=link)
            _row.append(inline_button)
        rows.append(_row)
    reply_markup = InlineKeyboardMarkup(rows)
    return reply_markup
