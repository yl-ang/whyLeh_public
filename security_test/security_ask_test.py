import nus_mod
import traceback

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


def sqli_ask_test():

    # Sqli security testing for ask
    try:
        print("Starting Sqli security testing for ask")
        assert ask_command(update_data("CS1101S ' --", "group"), True, "CS1101S") == "Question : cs1101s ' --, ID: 1\n"
        assert ask_command(update_data("CS1101S ' #", "group"), True, "CS1101S") == "Question : cs1101s ' #, ID: 1\n"
        assert ask_command(update_data("CS1101S ' AND 1=0 UNION ALL SELECT '*', '81dc9bdb52d04dc20036dbd8313ed055", "group"), True, "CS1101S") == "Question : cs1101s ' and 1=0 union all select '*', '81dc9bdb52d04dc20036dbd8313ed055, ID: 1\n"
        assert ask_command(update_data("CS1101S ') or ('1'='1", "group"), True, "CS1101S") == "Question : cs1101s ') or ('1'='1, ID: 1\n"
        assert ask_command(update_data("CS1101S ') or ('1'='1'/*" , "group") , True, "CS1101S") == "Question : cs1101s ') or ('1'='1'/*, ID: 1\n"
        assert ask_command(update_data("CS1101S 'or 1=1 or ''='", "group"), True, "CS1101S") == "Question : cs1101s 'or 1=1 or ''=', ID: 1\n"
        print("ask passed the sqli testing")
    except AssertionError as msg:
        print(traceback.print_exc())

sqli_ask_test()
