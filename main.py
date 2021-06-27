from bidict import bidict
import Constants as keys
from datetime import time as timer
import time
from TempDataBase import TempDB
from telegram.ext import *
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    Bot
)
import Responses as R
import requests
from tabulate import tabulate
import json
import nus_mod
from ChatIdDataBase import ChatIdDataBase


bot = Bot(keys.API_KEY)

# weds
# We need to think of a way to do the setup
# mod_grp_dict = bidict()

# This is how we get the list of mods from nus modules api, end of sem then run it
with open('nus_mods.json', 'rb') as input_file:
    input_dict = json.load(input_file)
    mod_list = [x["moduleCode"] for x in input_dict if x["moduleCode"] != ""]

    f = open("nus_mod.py", "w")
    f.write("nus_mod_lst = ")
    f.write(str(mod_list))
    f.close()

nus_mod_lst = nus_mod.nus_mod_lst

temp_db = TempDB()
chat_id_db = ChatIdDataBase()

print("Bot started ....")

question_database = {}

def get_module(txt):
    return txt.split()[1]

def valid_module(mod):
    return mod in nus_mod_lst

def check_grp_db(chat_id):
    return chat_id_db.check_chat_id(chat_id)
    ## new db.sqlite if the chat id is in.
    # return True/False

def start_command(update, context):
    
    grp_chat_id = update.message.chat_id 
    msg_chat_id = update.message.message_id
    chat_type = update.message.chat.type
    user_char_id = update.effective_user.id
    user_char_id = str(user_char_id)
    # bugged: didnt check if the user's is an admin or not

    if chat_type == "group" or chat_type == "supergroup":

        info_public_group_text = "To setup whyleh bot, you can do /start <module>"

        # check the admin status
        result = bot.get_chat_administrators(grp_chat_id)

        bot_rights = ""
        user_rights = ""
        for i in result:
            i = str(i)
            if "whyleh_bot" in i:
                if "administrator" in i:
                    bot_rights = "administrator"
                else:
                    bot_rights = "none"
            if user_char_id in i:
                if "administrator" in i:
                    user_rights = "administrator"
                else:
                    user_rights = "none"

        # bot_rights = bot.get_chat_member(grp_chat_id, ).status
        print(bot_rights)
        print(user_rights)

        if bot_rights != "administrator":
            print("Bot no rights")
            failure_start_bot_not_admin = "Please promote whyleh into an administrator."
            failure_start_bot_not_admin += "\n" + info_public_group_text
            update.message.reply_text(failure_start_bot_not_admin)

        if user_rights != "administrator":
            print("User no rights")
            failure_start_user_not_admin = "Only Administrator can use /Start."
            failure_start_user_not_admin += "\n" + info_public_group_text
            update.message.reply_text(failure_start_user_not_admin)
        else:
            try:
                module = get_module(str(update.message.text).lower()).upper()
            except:
                failure_start_no_mod = "Please enter a module!"
                update.message.reply_text(failure_start_no_mod)
            
            if valid_module(module):
                
                if check_grp_db(grp_chat_id):
                    failure_start_module_exist = "Bot has already setup."
                    update.message.reply_text(failure_start_module_exist)

                else:
                    chat_id_db.add_chatID(module, grp_chat_id, "True")
                    success_start_setup = "Bot successfully setup for %s " % module
                    update.message.reply_text(success_start_setup)
            else:
                failure_start_invalid_mod = "Please enter a valid module!"
                failure_start_invalid_mod += "\n" + info_public_group_text
                update.message.reply_text(failure_start_invalid_mod)
    else:
        start_text = '''
        Hi student, ask a question using /ask <module code> <Question>\nFor example, /ask CS1101S what is recursive process?
        '''
        update.message.reply_text(start_text)

def help_command(update, context):

    help_text = '''
    
    '''
    update.message.reply_text(help_text)

def send_message(chat_id, message):
        endpoint = f"https://api.telegram.org/bot{keys.API_KEY}/sendMessage"
        data = { "chat_id" : chat_id,
                    "text" : message}
        response = requests.post(endpoint, data=data)

def recent_command(update, context):

    # weds --> consider if else / or rm it from group chat 
    recent_text = "Select the module to search"
    grp_chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    msg_chat_id = update.message.message_id

    if chat_type == 'group' or chat_type == 'supergroup':

        grp_exist_status = check_grp_db(grp_chat_id)
        if grp_exist_status:
            module = chat_id_db.get_module(grp_chat_id)[0]
        else:
            failure_recent_grp_missing = "Please setup the bot using /start."
            update.message.reply_text(failure_recent_grp_missing)
        
    else:
        try:
            module = get_module(str(update.message.text).lower()).upper()
        except:
            failure_recent_no_mod = "Please enter a module!"
            update.message.reply_text(failure_recent_no_mod)
        
    if valid_module(module):
        grp_chat_id = update.message.chat_id
        # question = temp_db.get_questions(recent_mod, grp_chat_id)
        question = temp_db.get_questions(module)
        print(question)
        update.message.reply_text(tabulate(question, headers=["Id", "Questions"]))

    else:
        failure_recent = "Please enter a valid module code"
        print(failure_recent)
        update.message.reply_text(failure_recent)

def notify_command(update, context):
    question_id = str(update.message.text).lower().split()[1]
    if temp_db.qn_id_exist(question_id):
        user_id = update.effective_user.id
        temp_db.update_notification(question_id, user_id, "add")

    else:
        failure_question_id_notify = "Please enter a valid question id."
        update.message.reply_text(failure_question_id_notify)

def unnotify_command(update, context):

    question_id = str(update.message.text).lower().split()[1]
    if temp_db.qn_id_exist(question_id):
        user_id = update.effective_user.id
        temp_db.update_notification(question_id, user_id, "remove")
    else:
        failure_question_id_unnotify = "Please enter a valid question id."
        update.message.reply_text(failure_question_id_unnotify)


def daily_prompt(context: CallbackContext):

    # range_days = 86400 * 3
    
    #grp_chat_id = "-1001170563604"
    #module = chat_id_db.get_module(grp_chat_id)[0]
    #now_seconds = int(time.time())
    #unanswered_qns = temp_db.get_unanswered_qns(module, now_seconds - range_secconds)
    #bot.send_message(grp_chat_id,tabulate(unanswered_qns, headers=["Questions"]))
    range_secconds = 86400

    lst_chat_id = chat_id_db.get_chatID_daily_prompt()
    print(lst_chat_id)
    for grp_chat_id in lst_chat_id:
        print(grp_chat_id)
        module = chat_id_db.get_module(grp_chat_id[0])[0]
        print(module)
        now_seconds = int(time.time())
        unanswered_qns = temp_db.get_unanswered_qns(module, now_seconds - range_secconds)
        bot.send_message(grp_chat_id[0],tabulate(unanswered_qns, headers=["Today's unanswered questions"]))
    # update.message.reply_text(unanswered_qns)

    #https://stackoverflow.com/questions/59166469/how-to-schedule-a-telegram-bot-to-send-a-message
    #https://stackoverflow.com/questions/48288124/how-to-send-message-in-specific-time-telegrambot
    # send a daily summary of unanswered questions to the group
    # When to send it is depend on the admin and the frequently of the update (like maybe every 4 hours or a day)
    # we need to update temp db add 2 additional columns (user_id and answered)

    # what if different group has different daily prompt timing references???

def set_daily_prompt_command(update, context):
    grp_chat_id = update.message.chat_id 
    chat_type = update.message.chat.type

    if chat_type == 'group' or chat_type == 'supergroup':
        if chat_id_db.check_chat_id(grp_chat_id):
            chat_id_db.update_daily_prompt(grp_chat_id, "True")
            success_set_daily_prompt = "Daily Prompt has been set up successfully. Daily unanswered questions will be tallied and sent to the group every day"
            update.message.reply_text(success_set_daily_prompt)

        else:
            failure_recent_grp_missing = "Please setup the bot using /start."
            update.message.reply_text(failure_recent_grp_missing)

def stop_daily_prompt_command(update, context):
    grp_chat_id = update.message.chat_id 
    chat_type = update.message.chat.type

    if chat_type == 'group' or chat_type == 'supergroup':
        if chat_id_db.check_chat_id(grp_chat_id):
            chat_id_db.update_daily_prompt(grp_chat_id, "False")
            success_set_daily_prompt = "Daily Prompt has been stop."
            update.message.reply_text(success_set_daily_prompt)

        else:
            failure_recent_grp_missing = "Please setup the bot using /start."
            update.message.reply_text(failure_recent_grp_missing)

def view_command(update, context):
    resp = str(update.message.text).lower() # lambda expression to scap off the message id
    question_id = resp.split()[1]

    if temp_db.qn_id_exist(question_id):
        question = temp_db.get_question_from_id(question_id)[0][0]
        reply = temp_db.get_reply(question_id)
        full_response = "%s %s" % (str(question), str(reply))
        update.message.reply_text(full_response)

    else:
        failure_invalid_qn_id_reply = "Please enter a valid question id"
        update.message.reply_text(failure_invalid_qn_id_reply)

def retrieve_latest_id():
    # to map ugly id to nicer one
    # retrieve from db the latest own id
    qn_id = temp_db.get_qn_id()
    print(qn_id)
    if len(qn_id) > 0:
        return int(qn_id[0][0]) + 1
    else:
        return 1


def unit_test():
    # tbc
    pass

def search_command(update, context):
    
    # Work on this Thurs 17/6 ++ , see "LIKE"
    search_text = "Select the module to search"
    keyboard = [
        [
            InlineKeyboardButton("GER1000", callback_data='1'),
            InlineKeyboardButton("CS2030S", callback_data='2'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(search_text, reply_markup=reply_markup)

    print(update.callback_query.answer())


# UI features to consider:
# We can give user the choice to get notified or not (for example after they replied to the question)
# this can be done by inline keyboard actions.

# The notify button can be inserted below the question, giving other people the choice to be notified
# even if they didnt participate in the convo.


def ask_command(update, context):

    # result = retrieve_latest_id()
    # print(result)
    asked = str(update.message.text).lower()

    def get_question(txt, chat_type):
        print(txt.split())
        if chat_type == "private":
            return ' '.join(txt.split()[2:])
        else:
            return ' '.join(txt.split()[1:])

    grp_chat_id = update.message.chat_id 
    msg_chat_id = update.message.message_id
    chat_type = update.message.chat.type
    user_chat_id = update.effective_user.id

    if chat_type == "group" or chat_type == "supergroup":

        grp_exist_status = check_grp_db(grp_chat_id)

        if grp_exist_status:
            question = get_question(asked, chat_type)
            print(chat_id_db.get_module(grp_chat_id))
            module = chat_id_db.get_module(grp_chat_id)[0]
        else:
            failure_ask_grp_missing = "Please setup the bot using /start."
            update.message.reply_text(failure_ask_grp_missing)
    
    else:
        module = get_module(asked).upper()
        question = get_question(asked, chat_type)
        grp_chat_id = chat_id_db.get_chatID(module)[0]

    if len(question) > 0 and valid_module(module):

        qn_id = retrieve_latest_id()
        success_ask = "Question : %s, ID: %s " % (question, qn_id)
        message_id =  bot.send_message(grp_chat_id, success_ask).message_id
        time_seconds = update.message.date
        time_seconds = int(time_seconds.timestamp())
        temp_db.add_question(str(qn_id), module, grp_chat_id, message_id, success_ask, str(user_chat_id),"False", "", str(user_chat_id), time_seconds)

    else:
        failure_ask = "Please ask a valid question"
        update.message.reply_text(failure_ask)

def reply_command(update, context):

    resp = str(update.message.text).lower() # lambda expression to scap off the message id
    question_id = resp.split()[1]
    reply = '  '.join(resp.split()[2:])
    
    # update.message.reply_text("A\nB")
    if temp_db.qn_id_exist(question_id):
        message_id = temp_db.get_message_id(question_id)
        question = temp_db.get_question_from_id(question_id)[0][0]
        module = temp_db.get_module(question_id)[0][0]
        chat_id = chat_id_db.get_chatID(module)[0]

        # need to add a if else check for valid question id
        if len(reply) > 0:
            reply = "\nReply: %s" % (reply)
            temp_db.update_reply(question_id, reply)
            full_reply = temp_db.get_reply(question_id)
            print(full_reply)
            success_reply = "%s %s" % (question, full_reply)
            
            # need to consider resending the message and update the db to reply to it (since tele has message edit exp date)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=success_reply)

            #to notify indivual
            user_id = update.effective_user.id
            list_idv = temp_db.get_notification(question_id, user_id)
            message = "Someone replied to %s Question %s" % (module, question_id)
            for idv in list_idv:
                send_message(idv, message)
            temp_db.update_notification(question_id, user_id, "add")
        else:
            failure_empty_reply = "Please reply something."
            update.message.reply_text(failure_empty_reply)
    else:
        failure_invalid_qn_id_reply = "Please enter a valid question id"
        update.message.reply_text(failure_invalid_qn_id_reply)


def handle_message(update, context):
    text = str(update.message.text).lower()
    print("Message received from the user: %s " % text)

    resp = R.private_response(text)
    update.message.reply_text(resp)

def error_logging(update, context):

    print("Update %s caused error %s" % (update, context.error))

def main():
    temp_db.setup()
    chat_id_db.setup()
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("search", search_command))
    dp.add_handler(CommandHandler("ask", ask_command))
    dp.add_handler(CommandHandler("recent", recent_command))
    dp.add_handler(CommandHandler("reply", reply_command))
    dp.add_handler(CommandHandler("notify", notify_command))
    dp.add_handler(CommandHandler("unnotify", unnotify_command))
    dp.add_handler(CommandHandler("view", view_command))
    dp.add_handler(CommandHandler("set_daily", set_daily_prompt_command))
    dp.add_handler(CommandHandler("stop_daily", stop_daily_prompt_command))
    # dp.add_handler(CommandHandler("daily", daily_prompt, pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error_logging)
    job = updater.job_queue
    job.run_daily(daily_prompt, time=timer(hour = 11, minute = 59, second = 55),days=(0, 1, 2, 3, 4, 5, 6))
    updater.start_polling()
    updater.idle()

main()