import nus_mod

def update_data(args, grp_type):
    update = {
        'update_id': 111966803,
        'message': {
            'message_id': 50,
            'date': 1625239162,
            'chat': {
                'id': -1001583239230,
                'type': '%s' %grp_type,
                'title': 'ACC1006 Testing'
            },
            'text': '/start %s' %args,
            'entities': [{
                'type': 'bot_command',
                'offset': 0,
                'length': 6
            }],
            'caption_entities': [],
            'photo': [],
            'new_chat_members': [],
            'new_chat_photo': [],
            'delete_chat_photo': False,
            'group_chat_created': False,
            'supergroup_chat_created': False,
            'channel_chat_created': False,
            'from': {
                'id': 257677537,
                'first_name': 'Ang Yong Liang',
                'is_bot': False,
                'username': 'bobby_bob90',
                'language_code': 'en'
            }
        }
    }

    return update


nus_mod_lst = nus_mod.nus_mod_lst

def get_module(txt):
    return txt.split()[1]

def valid_module(mod):
    return mod in nus_mod_lst


# /start command for unit testing
def start_command(update, bot_right, admin_right, grp_exist):
    
    grp_chat_id = update['message']['chat']['id']
    msg_chat_id = update['message']['message_id']
    chat_type = update['message']['chat']['type']
    user_char_id = update['message']['from']['id']
    user_char_id = str(user_char_id)


    if chat_type == "group" or chat_type == "supergroup":

        info_public_group_text = "To setup whyleh bot, you can do /start <module>"

        bot_rights = bot_right
        user_rights = admin_right

        if bot_rights != "administrator":
            failure_start_bot_not_admin = "Please promote whyleh into an administrator."
            failure_start_bot_not_admin += "\n" + info_public_group_text
            return failure_start_bot_not_admin

        if user_rights != "administrator":
            failure_start_user_not_admin = "Only Administrator can use /Start."
            failure_start_user_not_admin += "\n" + info_public_group_text
            return failure_start_user_not_admin
        else:
            try:
                module = get_module(str(update['message']['text']).lower()).upper()
            except:
                failure_start_no_mod = "Please enter a module!"
                return failure_start_no_mod
            
            if valid_module(module):
                
                if grp_exist:
                    failure_start_module_exist = "Bot has already setup."
                    return failure_start_module_exist

                else:
                    success_start_setup = "Bot successfully setup for %s " % module
                    return success_start_setup
            else:
                failure_start_invalid_mod = "Please enter a valid module!"
                failure_start_invalid_mod += "\n" + info_public_group_text
                return failure_start_invalid_mod
    else:
        start_text= '''/ask <module> <Question>: Send and display a question to the group of the specified module.
/reply <module> <Question ID>: Reply to a question anonymously for the specified module.
/recent <module>: Retrieve and display the reecently asked questions with the [Question ID] for the specified module.
/view <Question ID>: Diplay the question with replies based on the Question ID.
/notify <question ID>: Enable notifications to a question based on the specified Question ID.
/unnotify <Question ID>: Disable notifications to a question based on the specified Question ID.
/help: Display the list of commands the bot can run.'''
        return start_text


def test_start():
    
    # New group, valid module, bot and user are administrators
    assert start_command(update_data("ACC1006", "supergroup"), "administrator", "administrator", False) == "Bot successfully setup for %s " % "ACC1006"
    assert start_command(update_data("ACC1006", "group"), "administrator", "administrator", False) == "Bot successfully setup for %s " % "ACC1006"

    # New group, valid module, user administrator but bot isnt
    assert start_command(update_data("ACC1006", "supergroup"), "user", "administrator", False) == "Please promote whyleh into an administrator.\nTo setup whyleh bot, you can do /start <module>"
    assert start_command(update_data("ACC1006", "group"), "user", "administrator", False) == "Please promote whyleh into an administrator.\nTo setup whyleh bot, you can do /start <module>"

    # New group, valid module, user isnt administrator but bot is
    assert start_command(update_data("ACC1006", "supergroup"), "administrator", "user", False) == "Only Administrator can use /Start.\nTo setup whyleh bot, you can do /start <module>"
    assert start_command(update_data("ACC1006", "group"), "administrator", "user", False) == "Only Administrator can use /Start.\nTo setup whyleh bot, you can do /start <module>"

    # New group, empty module, bot and user are administrators
    assert start_command(update_data("", "supergroup"), "administrator", "administrator", False) == "Please enter a module!"
    assert start_command(update_data("", "group"), "administrator", "administrator", False) == "Please enter a module!"

     # New group, invalid module, bot and user are administrators
    assert start_command(update_data("CS9999", "supergroup"), "administrator", "administrator", False) == "Please enter a valid module!\nTo setup whyleh bot, you can do /start <module>"
    assert start_command(update_data("CS9898", "group"), "administrator", "administrator", False) == "Please enter a valid module!\nTo setup whyleh bot, you can do /start <module>"

     # group has been setup already, valid module, bot and user are administrators
    assert start_command(update_data("ACC1006", "supergroup"), "administrator", "administrator", True) == "Bot has already setup."
    assert start_command(update_data("ACC1006", "group"), "administrator", "administrator", True) == "Bot has already setup."

     # private message, valid module, bot and user are administrators
    assert start_command(update_data("ACC1006", "private"), "administrator", "administrator", False) == '''/ask <module> <Question>: Send and display a question to the group of the specified module.
/reply <module> <Question ID>: Reply to a question anonymously for the specified module.
/recent <module>: Retrieve and display the reecently asked questions with the [Question ID] for the specified module.
/view <Question ID>: Diplay the question with replies based on the Question ID.
/notify <question ID>: Enable notifications to a question based on the specified Question ID.
/unnotify <Question ID>: Disable notifications to a question based on the specified Question ID.
/help: Display the list of commands the bot can run.'''
    

test_start()