# ตัวอย่างของ Chatbot API
# run with
#   uvicorn --host 0.0.0.0 --reload --port 3000 bot_api:app

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

import libs.Classification as cf
import libs.QA as qa
import libs.Chitchat as cc
import os
os.environ["CUDA_VISIBLE_DEVICES"]="0,1"


app = FastAPI()

chat_history = []

@app.get("/chat")
async def echo(line: str):
    global chat_history

    mode = cf.predict(line)

    user_input = f'QUEATION: {line} </s>'
    # user_input = f'{line} </s>'
    chat_history.append( user_input)

    while len(chat_history) > 5:
        chat_history.pop(0)

    if mode == 'chat_mode':
        text = cc.chat(user_input=user_input, chat_history=chat_history)
    else:
        text = qa.predict(quest=line)

    bot_output = f"ANSWER: {text} </s>"
    # bot_output = f"{text} </s>"

    chat_history.append(bot_output)

    return PlainTextResponse(text) # None = QA with no answer

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == '__main__':
    main()