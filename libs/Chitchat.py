
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM, AutoModelForQuestionAnswering

# tokenizer = AutoTokenizer.from_pretrained("kobkrit/openthaigpt-gpt2-instructgpt-poc-0.0.3")
# model = AutoModelForCausalLM.from_pretrained("kobkrit/openthaigpt-gpt2-instructgpt-poc-0.0.3")

# tokenizer = AutoTokenizer.from_pretrained("timpal0l/mdeberta-v3-base-squad2")

# model = AutoModelForCausalLM.from_pretrained("timpal0l/mdeberta-v3-base-squad2")

tokenizer = AutoTokenizer.from_pretrained("4s4ki/doodownnakumkuing")
model = AutoModelForSeq2SeqLM.from_pretrained("4s4ki/doodownnakumkuing")

# tokenizer = AutoTokenizer.from_pretrained("Pollawat/mt5-small-thai-qg")
# model = AutoModelForSeq2SeqLM.from_pretrained("Pollawat/mt5-small-thai-qg")

# chat_history = []
# Let's chat for 5 lines
def chat(user_input, chat_history):
    # global chat_history
    # print("")
    # user_input = f'QUEATION: {text} </s>'
    # chat_history.append( user_input + )

    # while len(chat_history) > 5:
    #     chat_history.pop(0)

    hist = ""
    for chat in chat_history:
        hist += "\n" + chat
    hist += "\nANSWER: "
    # hist += "\n"
    # print(hist)

    with torch.no_grad():
        # new_user_input_ids = tokenizer.encode(user_input, f'CONTEXT: {hist}', return_tensors='pt',  add_special_tokens=True)
        new_user_input_ids = tokenizer.encode(user_input, return_tensors='pt',  add_special_tokens=True)

        bot_input_ids = new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens, 
        chat_history_ids = model.generate(
            bot_input_ids, 
            max_length=512,
            num_beams=5,
            pad_token_id=tokenizer.eos_token_id,  
            do_sample=True, 
            top_p=50,
            top_k=20,
            temperature = 0.1,
            num_return_sequences=1,
        )

        bot_text = [ tokenizer.decode(chat_ids, 
                                      skip_special_tokens=True,
                                      clean_up_tokenization_spaces=True,)
                                      for chat_ids in chat_history_ids
                                      ]

    # bot_text = bot_text.replace("\n", " / ")
    
    # pretty print last ouput tokens from bot
    # print(">>Bot: {}".format(bot_text[0]))
    
    # chat_history.append("ANSWER: " + bot_text[0]+ tokenizer.eos_token)
    # print('chat history: {}'.format(' '.join(chat_history)))
    print(bot_text)

    return bot_text[0] if bot_text else ""
