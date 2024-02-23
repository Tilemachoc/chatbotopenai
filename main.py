import openai
from dotenv import find_dotenv, load_dotenv
import logging
from openai_func import *
from typing import Optional



# INITIALIZATION

'''load_dotenv()
client = openai.OpenAI()
openai_model = "gpt-3.5-turbo-16k"
assist_id = "asst_Iydh5lFCJn3e2U37sC5iPzDS"


logging.basicConfig(filename='example.log', level=logging.INFO)


# CREATE THREAD AND GET THE INTENT OF MESSAGE

instructions_data = {
    "card_info": None,
    "user_intent": "intent"
}


instructions_bool = False
INCOMMING_MESSAGE="<INCOMMING MESSAGE>"
#if the message is in a new chat:
thread_id = init_thread(client,message=INCOMMING_MESSAGE)
#if the message is in a chat with already created thread
thread = add_message(client,thread_id,message=INCOMMING_MESSAGE)
thread_id = thread.id
run_id = create_run(client,thread_id,assistant_id=assist_id,instructions_bool=instructions_bool)
wait_for_run_completion(client=client,thread_id=thread_id,run_id=run_id)


intent_list = [] #figure out how to extract list from data (you need to pay to print result, also see the tutorial)


message_card, message_intent = process_message(intent_list)

instructions_data["card_info"]=message_card
instructions_data["user_intent"]=message_intent


OUTGOING_MESSAGE,instructions_bool = find_and_call(message_intent,message_card,client,assist_id,thread_id)
'''

def generate_response(client: openai.OpenAI, message: str, assist_id: str, thread_id: Optional[str] = None, intent_thread_id: Optional[str] = None, instructions_bool: bool = False):
    intent_response = None

    if thread_id:
        thread = add_message(client,thread_id,message=message)
        thread_id = thread.id
        intent_thread = add_message(client,intent_thread_id,message=message)
        intent_thread_id = intent_thread_id
    else:
        thread_id = init_thread(client,message=message)
        intent_thread_id = init_thread(client,message=message)

    run_id = create_run(client=client,intent_thread_id=intent_thread_id,assistant_id=assist_id,instructions_bool=instructions_bool)
    intent_response = wait_for_run_completion(client=client,thread_id=intent_thread_id,run_id=run_id)
    a_index = intent_response.find("[")
    b_index = intent_response[a_index+1:].find("]")
    intent_list = intent_response[a_index:a_index+1+b_index+1]
    intent_list = eval(intent_list)
    message_card, message_intent = process_message(lst=intent_list,instructions_bool=instructions_bool)

    OUTGOING_MESSAGE,instructions_bool = find_and_call(message_intent=message_intent,message_card=message_card,client=client,assist_id=assist_id,thread_id=thread_id)


    result = {
        "message": OUTGOING_MESSAGE,
        "assist_id": assist_id,
        "thread_id": thread_id,
        "intent_thread_id": intent_thread_id,
        "instructions_bool": instructions_bool,
    }

    return result