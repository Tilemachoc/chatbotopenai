response = "hello this is ['card information given',1234561234]"
print(type(response), response)
a_index = response.find("[")
b_index = response[a_index+1:].find("]")
print(a_index,b_index,type(a_index),type(b_index))
intent_list = response[a_index:a_index+1+b_index+1]
print("process_message problem:",intent_list)
print(type(intent_list))
a = eval(intent_list)
for j in a:
    print(j)
for i in intent_list:
    print(i)
"""message_card, message_intent = intent_list
print("message_card:",message_card)
if not message_card.isdigit() or len(str(message_card)) != 10:
    message_card, message_intent = None, "intent"
    print("KAPPACHUNGUS")
"""
