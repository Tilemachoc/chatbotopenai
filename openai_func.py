import openai
import time
import logging 
from datetime import datetime
from typing import Text, Optional
import mysql.connector
import os
from dotenv import load_dotenv
import asyncio


load_dotenv()
sql_pass = os.getenv("sql_pass")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=sql_pass,
    database="chatbotmagna"
)

query = (
    "SELECT column_name "
    "FROM information_schema.columns "
    "WHERE table_schema = %s "
    "AND table_name = %s "
    "AND column_key = 'PRI'"
)

table_schema = "chatbotmagna"
table_name = "card_info"

cursor = conn.cursor()

cursor.execute(query,(table_schema,table_name))

primkey_column = cursor.fetchone()[0]

values_query = f"SELECT {primkey_column} FROM {table_name}"

cursor.execute(values_query)

primary_key_values = [row[0] for row in cursor.fetchall()]

#print(primary_key_values)

def wait_for_run_completion(client: openai.OpenAI,thread_id: Text,run_id: Text,sleep_interval=5):
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occured while retrieving the run: {e}")
            print(f"An error occured while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)
    return response


def init_thread(client: openai.OpenAI,message=None):
    if message:
        intent_thread = client.beta.threads.create(
            messages = [
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
    else:
        intent_thread = client.beta.threads.create()
    return intent_thread.id


def add_message(client: openai.OpenAI,thread_id,message):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    return client.beta.threads.retrieve(thread_id=thread_id)


def create_run(client: openai.OpenAI, intent_thread_id, assistant_id,instructions_bool=False):
    if instructions_bool:
        intent_instructions = """
    YOU SHOULD ONLY RETURN A LIST WITH NO EXPLANATION

    The default behavior of you is to return a list '''["intent", None]''' for most interactions. 
    
    ONCE YOU HAVE COLLECTED 10 DIGITS OF A CARD ONLY THEN CONSIDER THE FOLLOWING ELSE ONLY RETURN '''["intent", None]''':

    If you have collected the first six and last four digits of a card, you should return '''["card information given", 10-digit number]'''
    If the user explicitly confirms a refund, you should return '''["confirming refund", 10-digit number]'''


    YOU SHOULD ONLY RETURN A LIST WITH NO EXPLANATION
    """
    else:
        intent_instructions = """
    YOU SHOULD ONLY RETURN A LIST WITH NO EXPLANATION

    The default behavior of you is to return a list '''["intent", None]''' for most interactions. 
    
    ONCE YOU HAVE COLLECTED 10 DIGITS OF A CARD ONLY THEN CONSIDER THE FOLLOWING ELSE ONLY RETURN '''["intent", None]''':

    If you have collected the first six and last four digits of a card, you should return '''["card information given", 10-digit number]'''

    YOU SHOULD ONLY RETURN A LIST WITH NO EXPLANATION
    """
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=intent_thread_id,
        instructions=intent_instructions
    )
    return run.id



def process_message(lst,instructions_bool):
    message_intent = lst[0]
    message_card = lst[1]
    if isinstance(message_card, str) and message_card.isdigit() and len(message_card) == 10:
        return message_card, message_intent
    elif isinstance(message_card, int) and len(str(message_card)) == 10:
        return message_card, message_intent
    elif message_intent=="confirming refund" and instructions_bool==True:
        return message_card, message_intent
    else:

        return None, "intent"


def process_card(client,thread_id,card):
    card_formatted = str(card).replace(" ","")
    if card_formatted in primary_key_values:
        return explain_offer(client=client,thread_id=thread_id,card=card_formatted)
    else:
        return error_card(client=client,thread_id=thread_id,card=card_formatted)



def error_card(client,thread_id,card):
    thank_you = "Thank you for providing your card information. Please bear with me for a moment while I search for your details in our system."
    error = f"I apologize for the inconvenience, but it seems that there is no card located in our system with these digits: {card[:6]} {card[6:]}. Please double-check the information you provided to ensure its accuracy. If the information is correct and you're still unable to proceed, I recommend reaching out to our human support team for further assistance. They'll be able to investigate the issue more thoroughly and help resolve any issues you may be experiencing. Thank you for your patience and understanding."
    add_message(client=client,thread_id=thread_id,message=
                thank_you + error)
    return [error,False]


def explain_offer(client,thread_id,card):
    column_to_select = "product"
    query = (
        f"SELECT {column_to_select} FROM {table_name} "
        f"WHERE {primkey_column} = %s"
    )
    cursor.execute(query,(card,))
    result = cursor.fetchone()

    product = result[0]
    print(product)
    thank_you = "Thank you for providing your card information. Please bear with me for a moment while I search for your details in our system."
    explain = f'''I have located the charges on your card with digits: {card[:6]} {card[6:]}:

{product}

I'm sorry to inform you that we can only refund the charge for the Premium Membership as the product you bought has already been shipped.

Once refunded, the Premium Membership will be canceled so you will not be charged again in the future.

If you agree to the refund, please let me know and I will process it for you.'''
    add_message(client=client,thread_id=thread_id,message=
                thank_you+explain)
    return [explain,True]

#you have to first return them and then print them so you dont get the \n instead of the new lines:
#a,b = explain_offer("1234564321")
#print(a+b)

def confirm_refund(client,thread_id):
    thank_you = "Thank you for agreeing to the refund. Please bear with me for a moment while I process everything in our system."
    info = '''I have processed your request and refunded the charge as requested. The refund will be reflected on your account depending on your bank's processing time which can be up to 30 days.

I have also canceled your Premium Membership, so you can be assured that there will not be any further charges. You will receive an email confirmation of the above within 24 hours.'''
    contact = "Thank you for reaching out to us today. It has been a pleasure assisting you with your concern and I'm happy I was able to resolve your issue. For anything else, you may reach out to our email support team at support@MagnaStore.com"
    add_message(client=client,thread_id=thread_id,message=
                thank_you+info+contact)
    return [[info,contact],False]



def intent(client: openai.OpenAI,assist_id,thread_id):
    instructions = """You are assisting a customer customers who do not recognize charges on their credit cards. 
                            Please provide relevant information or assistance on these topics. Ensure that the responses are clear, concise, and helpful to the customer.
                            If the customer's question or statement is about irrelevant topics, politely acknowledge it with a brief apology.
                            In order to assist the user further ask them to provide the first 6 (six) and last 4 (four) digits of the card that was charged.
                            Make sure you collect all 10 (ten) digits."""
    run = client.beta.threads.runs.create(
        assistant_id=assist_id,
        thread_id=thread_id,
        instructions=instructions
    )
    response = wait_for_run_completion(client=client,thread_id=thread_id,run_id=run.id)
    #lgk response prepei na einai to text
    return [response,False]


def find_and_call(message_intent,message_card,client,assist_id,thread_id):
    if message_intent == "intent":
        return intent(client=client,assist_id=assist_id,thread_id=thread_id)
    elif message_intent == "card information given":
        return process_card(client=client,thread_id=thread_id,card=message_card)
    elif message_intent == "confirming refund":
        return confirm_refund(client,thread_id)
    else:
        raise NameError(f"message intent is not recognized: {message_intent}")