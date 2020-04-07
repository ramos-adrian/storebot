# No entry
from objects import ChatflowBuilder

wrong_1 = {"ent": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                          [{"text": "Button 2", "goto": "step3"},
                                                           {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# No entry text field
wrong_2 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"goto": "step2"}],
           "step1": [{"text": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                          [{"text": "Button 2", "goto": "step3"},
                                                           {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# No entry goto field
wrong_3 = {"entry": [{"entry_text": "TEXT HERE", "goto1": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                          [{"text": "Button 2", "goto": "step3"},
                                                           {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# Step has neither 'text' nor 'photo' field.
wrong_4 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text2": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                          [{"text": "Button 2", "goto": "step3"},
                                                           {"text": "Button 3", "goto": "step4"}]]}],
           "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# Keyboard is not a list.
wrong_5 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": True}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# Keyboard is not a list of lists.
wrong_6 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text2": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [{"text": "Button 1", "goto": "step2"},
                                                          {"text": "Button 2", "goto": "step3"},
                                                          {"text": "Button 3", "goto": "step4"}]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# Button in keyboard has no 'text' field.
wrong_7 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text2": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [[{"text2": "Button 1", "goto": "step2"}],
                                                          [{"text": "Button 2", "goto": "step3"},
                                                           {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# Button in keyboard has no 'goto' field.
wrong_8 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text2": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto2": "step2"}],
                                                          [{"text": "Button 2", "goto": "step3"},
                                                           {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# Inline keyboard is not a list.
wrong_9 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
           "step1": [{"text2": "TEXT HERE"},
                     {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                     {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                          [{"text": "Button 2", "goto": "step3"},
                                                           {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": True}]}

# Inline keyboard is not a list of lists.
wrong_10 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
            "step1": [{"text2": "TEXT HERE"},
                      {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                      {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                           [{"text": "Button 2", "goto": "step3"},
                                                            {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            {"text": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"},
            {"text": "link", "link": "http://google.com"}]}]}

# Button in inline keyboard has no 'text' field.
wrong_11 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
            "step1": [{"text2": "TEXT HERE"},
                      {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                      {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                           [{"text": "Button 2", "goto": "step3"},
                                                            {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text2": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}

# Button in inline keyboard has neither 'edit_text' nor 'link' field.
wrong_12 = {"entry": [{"entry_text": "TEXT HERE", "goto": "step1"}, {"entry_text": "OTHER TEXT", "goto": "step2"}],
            "step1": [{"text2": "TEXT HERE"},
                      {"text": "CAPTION", "photo": "https://telegra.ph/file/099311bbd0039ce13e59a.png"},
                      {"text": "TEXT HERE 2", "keyboard": [[{"text": "Button 1", "goto": "step2"}],
                                                           [{"text": "Button 2", "goto": "step3"},
                                                            {"text": "Button 3", "goto": "step4"}]]}], "step2": [
        {"text": "TEXT HERE", "inline_keyboard": [
            [{"text2": "Edit the text", "edit_text": "NEW TEXT HERE", "link_preview": False, "tag": "TAG2"}],
            [{"text": "link", "link": "http://google.com"}]]}]}


assert not ChatflowBuilder.verify_integrity(wrong_1)[0]
assert not ChatflowBuilder.verify_integrity(wrong_2)[0]
assert not ChatflowBuilder.verify_integrity(wrong_3)[0]
assert not ChatflowBuilder.verify_integrity(wrong_4)[0]
assert not ChatflowBuilder.verify_integrity(wrong_5)[0]
assert not ChatflowBuilder.verify_integrity(wrong_6)[0]
assert not ChatflowBuilder.verify_integrity(wrong_7)[0]
assert not ChatflowBuilder.verify_integrity(wrong_8)[0]
assert not ChatflowBuilder.verify_integrity(wrong_9)[0]
assert not ChatflowBuilder.verify_integrity(wrong_10)[0]
assert not ChatflowBuilder.verify_integrity(wrong_11)[0]
assert not ChatflowBuilder.verify_integrity(wrong_12)[0]
