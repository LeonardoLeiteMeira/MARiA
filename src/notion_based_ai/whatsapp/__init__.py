# poetry run uvicorn notion_based_ai.whatsapp:app --reload
import os
from fastapi import FastAPI
import httpx
from dotenv import load_dotenv

from notion_based_ai.MARiA import send_message


load_dotenv()

evolution_api_key = os.getenv("AUTHENTICATION_API_KEY")
app = FastAPI()

def get_maria_response(user_message: str):
    return send_message(user_message)

async def send_whatsapp_message(to:str, message: str):
    try:
        print("Enviando mensagem....")
        instance = 'maria'
        base_url = f"http://localhost:8080/message/sendText/{instance}"
        body = {
            "number": to,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "text": f"MARiA: {message}"
        }
        headers = {"apikey": evolution_api_key}

        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, json=body, headers=headers)
            print("Mensagem enviada: ", response)
    except Exception as e:
        print("Error: ", e)
    

@app.post('/whatsapp')
async def root(data: dict):
    print(data)
    if data['event'] == 'messages.upsert' and (not data['data']['key']['fromMe']):
        to = data['data']['key']['remoteJid']
        message_text = get_maria_response(data['data']['message']['conversation'])
        await send_whatsapp_message(to, message_text)

    return {'hello':'world'}