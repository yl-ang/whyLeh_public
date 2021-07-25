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
            'text': '/reply 1234567 %s' %args,
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


def reply_command(update, qn_id_exist, answered, list_idv):

    resp = str(update['message']['text']).lower() # lambda expression to scap off the message id
    question_id = resp.split()[1]
    reply = '  '.join(resp.split()[2:])

    if qn_id_exist:
        message_id = 9999
        question = "What is unit testing?"
        module = "ACC1006"
        chat_id = -1001583239230

        # need to add a if else check for valid question id
        if len(reply) > 0:
            reply = "\nReply: %s\n" % (reply)
            
            full_reply = "A type of software testing where individual units or components of a software are tested."

            success_reply = "%s %s" % (question, full_reply)

            message = "Someone replied to %s Question %s" % (module, question_id)

            author_id = 666666666666

            for idv in list_idv:

                if idv == author_id and answered == False:
                    author_messsage = "Someone replied to %s Question %s \n \nPlease enter /answered %s if your question has been answered" % (module, question_id, question_id)
                    return author_messsage
                else:
                    return message
        else:
            failure_empty_reply = "Please reply something."
            return failure_empty_reply

    else:
        failure_invalid_qn_id_reply = "Please enter a valid question id"
        return failure_invalid_qn_id_reply

def sqli_ask_test():

    # Sqli security testing for reply
    try:
        print("Starting Sqli security testing for ask")
        assert reply_command(update_data("89' --", "group"), False, False , [666666666666]) == "Please enter a valid question id"
        assert reply_command(update_data("89'/*", "group"), False, False , [666666666666]) == "Please enter a valid question id"
        assert reply_command(update_data("89' or '1'='1", "group"), False, False , [666666666666]) == "Please enter a valid question id"
        assert reply_command(update_data("89' or '1'='1'#", "group"), False, False , [666666666666]) == "Please enter a valid question id"
        assert reply_command(update_data("89') or ('1'='1'--", "group"), False, False , [666666666666]) == "Please enter a valid question id"
        assert reply_command(update_data("89') or ('1'='1'/*", "group"), False, False , [666666666666]) == "Please enter a valid question id"
        assert reply_command(update_data("100 ' AND 1=0 UNION ALL SELECT '*', '81dc9bdb52d04dc20036dbd8313ed055' --", "group"), False, False , [666666666666]) == "Please enter a valid question id"
        print("reply passed the sqli testing")
    except AssertionError:
        print(traceback.print_exc())

sqli_ask_test()