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
            'text': '/ask %s' %args,
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


def ask_command(update, group_exist, module):

    # result = retrieve_latest_id()
    # print(result)
    asked = str(update['message']['text']).lower()

    def get_question(txt, chat_type):
        if chat_type == "private":
            return ' '.join(txt.split()[2:])
        else:
            return ' '.join(txt.split()[1:])

    grp_chat_id = update['message']['chat']['id']
    msg_chat_id = update['message']['message_id']
    chat_type = update['message']['chat']['type']
    user_char_id = update['message']['from']['id']
    user_char_id = str(user_char_id)

    if chat_type == "group" or chat_type == "supergroup":

        grp_exist_status = group_exist

        if grp_exist_status:
            question = get_question(asked, chat_type)
            module = module
        else:
            failure_ask_grp_missing = "Please setup the bot using /start."
            return failure_ask_grp_missing
    
    else:
        module = get_module(asked).upper()
        question = get_question(asked, chat_type)

    if len(question) > 0 and valid_module(module) and group_exist:

        qn_id = 1
        success_ask = "Question : %s, ID: %s\n" % (question, qn_id)
        return success_ask

    else:
        if not valid_module(module):
            failure_invalid_module = "The module %s you have entered do not exist" % module
            return failure_invalid_module

        else:
            if not group_exist:
                failure_group_not_exist = "The %s group may not exist or has not set up the WhyLeh bot" % module
                return failure_group_not_exist

            else:
                if len(question) == 0:
                    failure_ask = "Please ask a valid question"
                    return failure_ask

def test_ask():
    # group exist with proper question
    assert ask_command(update_data("Hello", "group"), True, "ACC1006") == "Question : hello, ID: 1\n"

    # group do not exist with proper question
    assert ask_command(update_data("Hello", "group"), False, "ACC1006") == "Please setup the bot using /start."

    # group exist without proper question
    assert ask_command(update_data("", "group"), True, "ACC1006") == "Please ask a valid question"

    # group do not exiist with out proper question
    assert ask_command(update_data("", "group"), False, "ACC1006") == "Please setup the bot using /start."

    # private message exist with proper question
    assert ask_command(update_data("ACC1006 Hello", "private"), True, "ACC1006") == "Question : hello, ID: 1\n"

    # private message without proper question
    assert ask_command(update_data("ACC1006", "private"), True, "ACC1006") == "Please ask a valid question"

    # private message witth group do not exist
    assert ask_command(update_data("ACC1006", "private"), False, "ACC1006") == "The ACC1006 group may not exist or has not set up the WhyLeh bot"

    #private message with invalid module
    assert ask_command(update_data("ACC1006", "private"), False, "ACC0000") == "The module ACC0000 you have entered do not exist"


    

test_ask()