import random

def private_response(input_text):
    user_message = str(input_text).lower()

    if user_message in  ("hi", "hello", "sup"):

        hello_msg = [
            '''Hi student, you can ask me for the recently asked questions in modules by doing /recent <module_code>. For example /recent CS1101S''',
            '''Hey there , do you know you can ask questions by doing /reply <module_code> <id>. For example /reply CS2030S 2'''
            ]
        
        return hello_msg[random.randint(0,len(hello_msg))]

    elif user_message in ("who are you", "who are you?"):
        intro_msg = "I am WhyLeh! A study chat bot to organise questions and responses ^-^"
        return intro_msg

    elif True:
        pass
    else:
        return "I don't quite understand you, do /help for more commands."

