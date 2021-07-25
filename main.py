from os import truncate
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
import math
from ChatIdDataBase import ChatIdDataBase
from profanity_filter import ProfanityFilter
from captcha.image import ImageCaptcha
import random
from base64 import b64encode
from io import BytesIO

bot = Bot(keys.API_KEY)


pf = ProfanityFilter(languages=['en'])

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

captcha_count = 1
question_database = {}
captcha_lst = {}
def get_module(txt):
    return txt.split()[1]

def valid_module(mod):
    return mod in nus_mod_lst

def check_grp_db(chat_id):
    return chat_id_db.check_chat_id(chat_id)
    ## new db.sqlite if the chat id is in.
    # return True/False

def random_image_captcha():

    words="123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
    noisecurve_number=1
    noisedot_width=6
    noisedot_number=32
    length=6
    n, key = len(words), ""
    generator = ImageCaptcha(width=290,height=60)

    for i in range(length):
        key += words[random.randint(0, n-1)]

    rgb = (random.randint(0, 256), random.randint(0,
                                                  256), random.randint(0, 256))
    b_rgb = (random.randint(0,
                            256), random.randint(0,
                                                 256), random.randint(0, 256))
    
    img = generator.create_captcha_image(key, rgb, background=b_rgb)

    for i in range(noisecurve_number):
        img = generator.create_noise_curve(img, rgb)
    
    img = generator.create_noise_dots(img, rgb, noisedot_width, noisedot_number)
    bio = BytesIO()
    bio.name = 'image.jpeg'
    img.save(bio, format='JPEG')
    bio.seek(0)
    return key, bio

def check_and_send_captcha(chat_id, user_chat_id):
    global captcha_count
    if captcha_count == 10:
        key, bio = random_image_captcha()
        bot.send_photo(chat_id, photo=bio)
        print(key)
        captcha_lst[user_chat_id] = str(key)
        captcha_count = 0
    else:
        captcha_count = captcha_count + 1


def captcha_command(update, context):

    # Only works for private
    # check if the user id is inside the captcha list
    user_char_id = update.effective_user.id
    chat_type = update.message.chat.type
    resp = str(update.message.text)

    if chat_type == "group" or chat_type == "supergroup":
        pass
    else:
        if user_char_id in captcha_lst:
            # we want to check if the parsed in key is the same
            correct_key = captcha_lst[user_char_id].lower()
            user_input_key = ' '.join(resp.split()[1:]).lower()
            # need to scape the key from the user reply

            if correct_key == user_input_key:
                success_captcha_pass_test = "You can now continue using whyleh."
                update.message.reply_text(success_captcha_pass_test)
                del captcha_lst[user_char_id]
            else:
                failure_captcha_fail_test = "Please try again."
                update.message.reply_text(failure_captcha_fail_test)

        else:
            failure_captcha_user_not_found = "You are not required to do captcha."
            update.message.reply_text(failure_captcha_user_not_found)
        

def sliced_text_lst(text):
    max_size = 4096
    amt_sized = math.ceil(len(text) / max_size)
    lst = []
    for i in range(0,amt_sized):
        lst.append(text[max_size * i: max_size * (i + 1)])
    return lst

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
                if "administrator" in i or "creator" in i:
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
                failure_start_no_mod = "Please enter a module!\n \nTo set up the bot, enter /start <Module>"
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
        start_text= '''/start: Display the list of commands the bot can run.
/search <module> <Search terms>: Search for similar past questions and replies
/ask <module> <Question>: Send and display a question to the group of the specified module.
/reply <module> <Question ID>: Reply to a question anonymously for the specified module.
/recent <module>: Retrieve and display the recently asked questions with the [Question ID] for the specified module.
/view <Question ID>: Display the question with replies based on the Question ID.
/notify <question ID>: Enable notifications to a question based on the specified Question ID.
/unnotify <Question ID>: Disable notifications to a question based on the specified Question ID.
/check <module>: Check whether the module has set up WhyLeh bot and get the invite link to the group'''
        update.message.reply_text(start_text)

def help_command(update, context):

    chat_type = update.message.chat.type

    if chat_type == "group" or chat_type == "supergroup":
        help_text= '''/start <Module code>: Set up the bot
/ask: Ask a question
/reply <Question ID>: Reply specific question with the Question ID
/view <Question ID>: View entire question and response of the specific Question ID
/recent: View recently a list of recently asked questions
/notify <Question ID>: Get notification when someone respnse to the specific question
/unnotify <Question ID>: Stop notification for the specific question
/set_daily: Display daily notification on the list of unanswered questions
/stop_daily: Stop daily notification on the list of unanswered questions
/check <module>: Check whether the module has set up WhyLeh bot and get the invite link to the group

To fully utillise the function, please start bot (https://t.me/whyleh_bot) privately'''
    else:
        help_text= '''/start: Display the list of commands the bot can run.
/search <module> <Search terms>: Search for similar past questions and replies
/ask <module> <Question>: Send and display a question to the group of the specified module.
/reply <module> <Question ID>: Reply to a question anonymously for the specified module.
/recent <module>: Retrieve and display the recently asked questions with the [Question ID] for the specified module.
/view <Question ID>: Display the question with replies based on the Question ID.
/notify <question ID>: Enable notifications to a question based on the specified Question ID.
/unnotify <Question ID>: Disable notifications to a question based on the specified Question ID.
/check <module>: Check whether the module has set up WhyLeh bot and get the invite link to the group'''
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
            failure_recent_no_mod = "Please enter a module! \n \nTo use the recent command, enter /recent <Module>"
            update.message.reply_text(failure_recent_no_mod)
        
    if valid_module(module):
        grp_chat_id = update.message.chat_id
        # question = temp_db.get_questions(recent_mod, grp_chat_id)
        question = temp_db.get_questions(module)
        print(question)
        
        questions = []
        for i in question:
            if len(i[1]) > 100:
                truncated = i[1][:100] + "..."
                questions.append((i[0], truncated))
            else:
                questions.append((i[0], i[1]))

        update.message.reply_text(tabulate(questions, headers=["Id", "Questions"])  + "\n\nUse /view ID to view the full question and answer.")
        # update.message.reply_text(tabulate(question, headers=["Id", "Questions"]))

    else:
        failure_recent = "Please enter a valid module code"
        print(failure_recent)
        update.message.reply_text(failure_recent)

def notify_command(update, context):
    resp = str(update.message.text).lower().split()
    if len(resp) > 1:
        question_id = resp[1]
        if temp_db.qn_id_exist(question_id):
            user_id = update.effective_user.id
            temp_db.update_notification(question_id, user_id, "add")

        else:
            failure_question_id_notify = "Please enter a valid question id."
            update.message.reply_text(failure_question_id_notify)
    else:
        failure_no_question_id = "Please enter the question id. \n \nTo use the notify command, enter /notify <Question ID>"
        update.message.reply_text(failure_no_question_id)

def unnotify_command(update, context):
    resp = str(update.message.text).lower().split()
    if len(resp) > 1:
        question_id = resp[1]
        if temp_db.qn_id_exist(question_id):
            user_id = update.effective_user.id
            temp_db.update_notification(question_id, user_id, "remove")
        else:
            failure_question_id_unnotify = "Please enter a valid question id."
            update.message.reply_text(failure_question_id_unnotify)
    
    else:
        failure_no_question_id = "Please enter the question id. \n \nTo use the unnotify command, enter /unnotify <Question ID>"
        update.message.reply_text(failure_no_question_id)


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
    resp = str(update.message.text).lower().split() # lambda expression to scap off the message id

    if len(resp) > 1:

        question_id = resp[1]
        if temp_db.qn_id_exist(question_id):
            chat_type = update.message.chat.type

            if chat_type == 'group' or chat_type == 'supergroup':
                grp_chat_id = update.message.chat_id
                grp_exist = chat_id_db.check_chat_id(grp_chat_id)

                if grp_exist:
                    module = chat_id_db.get_module(grp_chat_id)[0]
                    valid_module_qn_id = temp_db.check_module_qn_id(module, question_id)
                    if valid_module_qn_id:
                        question = temp_db.get_question_from_id(question_id)[0][0]
                        reply = temp_db.get_reply(question_id)
                        full_response = "%s %s" % (str(question), str(reply))

                        sliced_response = sliced_text_lst(full_response)

                        for i in sliced_response:
                            bot.send_message(grp_chat_id, i)

                    else:
                        failure_invalid_module_qn_id = "The question ID does not belong to this module"
                        update.message.reply_text(failure_invalid_module_qn_id)

                else:
                    failure_set_up = "Please set up the WhyLeh bot using /start <Module code>"
                    update.message.reply_text(failure_set_up)
            
            else:
                user_chat_id = update.effective_user.id
                question = temp_db.get_question_from_id(question_id)[0][0]
                reply = temp_db.get_reply(question_id)
                full_response = "%s %s" % (str(question), str(reply))

                sliced_response = sliced_text_lst(full_response)

                for i in sliced_response:
                    bot.send_message(user_chat_id, i)

        else:
            failure_invalid_qn_id_reply = "Please enter a valid question id"
            update.message.reply_text(failure_invalid_qn_id_reply)
    else:
        failure_no_qn_id = "Please enter the question id. \n \nTo use the view command, enter /view <Question ID>"
        update.message.reply_text(failure_no_qn_id)

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


# UI features to consider:
# We can give user the choice to get notified or not (for example after they replied to the question)
# this can be done by inline keyboard actions.

# The notify button can be inserted below the question, giving other people the choice to be notified
# even if they didnt participate in the convo.


def ask_command(update, context):
    # temp_db.search_db_qn()
    # result = retrieve_latest_id()
    # print(result)
    asked = str(update.message.text).lower()
    resp = str(update.message.text).split()

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
            
            if len(resp) > 1:
                question = get_question(asked, chat_type)
                module = chat_id_db.get_module(grp_chat_id)[0]
                if valid_module(module):
                    grp_chat_id = chat_id_db.get_chatID(module)[0]
                    qn_id = retrieve_latest_id()
                    success_ask = "Question : %s, ID: %s\n" % (question, qn_id)
                    success_ask = pf.censor(success_ask)
                    sliced_ask = sliced_text_lst(success_ask)

                    for i in sliced_ask:
                        message_id =  bot.send_message(grp_chat_id, i).message_id

                    time_seconds = update.message.date
                    time_seconds = int(time_seconds.timestamp())
                    temp_db.add_question(str(qn_id), module, grp_chat_id, message_id, success_ask, str(user_chat_id),"False", "", str(user_chat_id), time_seconds)

            else:
                failure_ask = "Please enter the question you would like to ask.\n \nTo use the ask command, enter /ask <Question>"
                update.message.reply_text(failure_ask)
                
        else:
            failure_ask_grp_missing = "Please setup the bot using /start."
            update.message.reply_text(failure_ask_grp_missing)

        

    else:
        check_and_send_captcha(grp_chat_id, user_chat_id)
        print(captcha_lst)
        

        if user_chat_id in captcha_lst:
            failure_capcha_test = "Please complete the capcha first.\nEnter the following command /captcha <answer> to complete the captcha."
            update.message.reply_text(failure_capcha_test)

        else:
            if len(resp) > 2:
                module = get_module(asked).upper()
                question = get_question(asked, chat_type)
                grp_exist = chat_id_db.check_module(module)
                if valid_module(module) and grp_exist:

                    grp_chat_id = chat_id_db.get_chatID(module)[0]
                    qn_id = retrieve_latest_id()
                    success_ask = "Question : %s, ID: %s\n" % (question, qn_id)
                    message_id =  bot.send_message(grp_chat_id, success_ask).message_id
                    time_seconds = update.message.date
                    time_seconds = int(time_seconds.timestamp())
                    temp_db.add_question(str(qn_id), module, grp_chat_id, message_id, success_ask, str(user_chat_id),"False", "", str(user_chat_id), time_seconds)
                    success_private_ask = "Your question has been sent to the group"
                    update.message.reply_text(success_private_ask)

                else:
                    if not valid_module(module):
                        failure_invalid_module = "The module %s you have entered do not exist" % module
                        update.message.reply_text(failure_invalid_module)

                    elif not grp_exist:
                        failure_group_not_exist = "The %s group may not exist or has not set up the WhyLeh bot" % module
                        update.message.reply_text(failure_group_not_exist)

            else:
                if len(resp) == 1:
                    failure_no_mod_question = "Please enter the module and question you would like to ask.\n \nTo use the ask command, enter /ask <Module> <Question>"
                    update.message.reply_text(failure_no_mod_question)

                elif len(resp) == 2:
                    failure_no_question = "Please enter the question you would like to ask.\n \nTo use the ask command, enter /ask <Module> <Question>"
                    update.message.reply_text(failure_no_question)

def reply_command(update, context):
    resp = str(update.message.text).lower().split() # lambda expression to scap off the message id
    if len(resp) > 2:
        question_id = resp[1]
        reply = '  '.join(resp[2:])
        reply = pf.censor(reply)
        # update.message.reply_text("A\nB")
        if temp_db.qn_id_exist(question_id):
            message_id = temp_db.get_message_id(question_id)
            question = temp_db.get_question_from_id(question_id)[0][0]
            module = temp_db.get_module(question_id)[0][0]
            chat_id = chat_id_db.get_chatID(module)[0]
            chat_type = update.message.chat.type
            user_chat_id = update.effective_user.id
            grp_chat_id = update.message.chat_id
            captcha_boo_checker = True

            if chat_type == "group" or chat_type == "supergroup":
                
                module = chat_id_db.get_module(grp_chat_id)[0]
            else:
                check_and_send_captcha(grp_chat_id, user_chat_id)
                if user_chat_id in captcha_lst:
                    captcha_boo_checker = False

            # need to add a if else check for valid question id
            if captcha_boo_checker:
                if len(reply) > 0 and temp_db.check_module_qn_id(module, question_id):

                    question = temp_db.get_question_from_id(question_id)[0][0]
                    old_reply = temp_db.get_reply(question_id)
                    old_full_reply = "%s %s" % (str(question), str(old_reply))

                    print(temp_db.check_module_qn_id(module, question_id))
                    reply = "\nReply: %s\n" % (reply)
                    temp_db.update_reply(question_id, reply)
                    full_reply = temp_db.get_reply(question_id)
                    print(full_reply)
                    success_reply = "%s %s" % (question, full_reply)

                    sliced_old_reply = sliced_text_lst(old_full_reply)
                    sliced_new_reply = sliced_text_lst(success_reply)

                    if len(sliced_old_reply) == len(sliced_new_reply):
                        
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=sliced_new_reply[-1])

                    else:
                        for i in sliced_new_reply:
                            new_message_id =  bot.send_message(grp_chat_id, i).message_id
                        # update the new message id for the question in db
                        temp_db.update_message_id(new_message_id, question_id)

                    # need to consider resending the message and update the db to reply to it (since tele has message edit exp date)
                    #to notify indivual
                    user_id = update.effective_user.id
                    list_idv = temp_db.get_notification(question_id, user_id)
                    message = "Someone replied to %s Question %s" % (module, question_id)
                    author_id = temp_db.get_author(question_id)
                    answered = temp_db.check_answered(question_id)
                    for idv in list_idv:
                        if idv == author_id and answered == 'False':
                            author_messsage = "Someone replied to %s Question %s \n \nPlease enter /answered %s if your question has been answered" % (module, question_id, question_id)
                            send_message(idv, author_messsage)
                        else:
                            send_message(idv, message)
                    temp_db.update_notification(question_id, user_id, "add")
                else:
                    if len(reply) == 0:
                        failure_empty_reply = "Please reply something."
                        update.message.reply_text(failure_empty_reply)
                    else:
                        failure_qn_id_module_not_match = "The question id does not belong to the group"
                        update.message.reply_text(failure_qn_id_module_not_match)
            else:
                failure_reply_captcha_test = "Please complete the capcha first.\nEnter the following command /captcha <answer> to complete the captcha."
                update.message.reply_text(failure_reply_captcha_test)


        else:
            failure_invalid_qn_id_reply = "Please enter a valid question id"
            update.message.reply_text(failure_invalid_qn_id_reply)
    else:
        if len(resp) == 1:
            failure_no_qn_id_reply = "Please enter the Question ID and reply.\n \nTo use the reply command, enter /reply <Qn ID> <Reply>"
            update.message.reply_text(failure_no_qn_id_reply)

        elif len(resp) ==2:
            failure_no_question = "Please enter the reply.\n \nTo use the reply command, enter /reply <Qn ID> <Reply>"
            update.message.reply_text(failure_no_question)

def answered_command(update, context):
    resp = str(update.message.text).lower().split()
    if len(resp) > 1:
        question_id = resp[1]
        user_chat_id = update.effective_user.id
        if temp_db.qn_id_exist(question_id):
            author_id = temp_db.get_author(question_id)
            if author_id == str(user_chat_id):
                temp_db.update_question(question_id, "True")
                success_answered = "Thank You, Question %s has been marked as answered" % question_id
                update.message.reply_text(success_answered)

            else:
                failure_author = "Sorry, only author of this question can mark it as answered"
                update.message.reply_text(failure_author)

        else:
            failure_invalid_qn_id_reply = "Please enter a valid question id"
            update.message.reply_text(failure_invalid_qn_id_reply)
    else:
        failure_no_qn_id = "Please enter the Question ID.\n \nTo use the answered command, enter /answered <Qn ID>"
        update.message.reply_text(failure_no_qn_id)

def search_command(update, context):
    resp = str(update.message.text).lower()
    chat_type = update.message.chat.type

    if chat_type != 'private':
        failure_not_private = "This command is only available on private message. Please use the search command (https://t.me/whyleh_bot) privately "
        update.message.reply_text(failure_not_private)

    else:
        check_resp = resp.split()
        if len(check_resp) > 2:
            module = get_module(resp).upper()
            search_item = '  '.join(resp.split()[2:])
            grp_exist = chat_id_db.check_module(module)

            if len(search_item) > 0 and valid_module(module) and grp_exist:
                question = temp_db.search_db_qn(module, search_item)
                questions = []
                qn_id =  []
                for i in question:
                    if i[0] not in qn_id:
                        if len(i[1]) > 100:
                            truncated = i[1][:100] + "..."
                            questions.append((i[0], truncated))
                        else:
                            questions.append((i[0], i[1]))
                        qn_id.append(i[0])
                if len(questions) == 0:
                    no_result = "Sorry, there is no great match for your search"
                    update.message.reply_text(no_result)
                else:
                    update.message.reply_text(tabulate(questions, headers=["Id", "Questions"])  + "\n\nUse /view ID to view the full question and answer.")

            else:
                if not valid_module(module):
                    failure_invalid_module = "The module %s you have entered do not exist" % module
                    update.message.reply_text(failure_invalid_module)

                elif not grp_exist:
                    failure_group_not_exist = "The %s group may not exist or has not set up the WhyLeh bot" % module
                    update.message.reply_text(failure_group_not_exist)

                elif len(search_item) == 0:
                    failure_search = "Please ask a valid question"
                    update.message.reply_text(failure_search)
        else:
            if len(check_resp) == 1:
                failure_no_mod_query = "Please enter the module and the query you would like to search.\n \nTo use the search command, enter /search <Module> <Search Term>"
                update.message.reply_text(failure_no_mod_query)

            elif len(check_resp) == 2:
                failure_no_query = "Please enter what you would like to search.\n \nTo use the search command, enter /search <Module> <Search Term>"
                update.message.reply_text(failure_no_query)

def check_command(update, context):
    resp = str(update.message.text).lower()
    check_resp = resp.split()
    if len(check_resp) > 1:
        module = get_module(resp).upper()
        valid_mod = valid_module(module)
        if valid_mod:
            group_exist = chat_id_db.check_module(module)
            
            if group_exist:
                chat_id = chat_id_db.get_chatID(module)
                invite_link = bot.getChat(chat_id[0]).invite_link
                success_bot_setup = "The bot has been setup for %s \n \nPlease use this link %s to join the group" % (module, invite_link)
                update.message.reply_text(success_bot_setup)

            else:
                failure_group_not_setup = "The bot has not been setup for %s" % module
                update.message.reply_text(failure_group_not_setup)

        else:
            failure_invalid_module = "The module %s you have entered do not exist" % module
            update.message.reply_text(failure_invalid_module)

    else:
        failure_no_module = "Please enter the module you would like to check.\n \nTo use the check command, enter /check <Module>"
        update.message.reply_text(failure_no_module)


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
    dp.add_handler(CommandHandler("answered", answered_command))
    dp.add_handler(CommandHandler("check", check_command))
    dp.add_handler(CommandHandler("captcha", captcha_command))
    # dp.add_handler(CommandHandler("daily", daily_prompt, pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error_logging)
    job = updater.job_queue
    job.run_daily(daily_prompt, time=timer(hour = 5, minute = 50, second = 55),days=(0, 1, 2, 3, 4, 5, 6))
    updater.start_polling()
    updater.idle()

main()