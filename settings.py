lang = {}
dispatcher = None
job_queue = None
# This handler activates everytime a user send a message that is not related to any chaflow or predefined handler
user_menu_popup_handler = None

# In this dictionary all active chatflows must be registered. The dictionary must have the following format:
# {name_1: conversation_handler, name_2: conversation_handler, ...}
registered_chatflows = {}

database = None

# Define here global variables as None and then initialize it the first time you use it
# For example:
# my_var = None

# Define here functions to get and set configurations in database
