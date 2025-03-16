# poetry run uvicorn notion_based_ai.whatsapp:app --reload
import os
from fastapi import FastAPI
import httpx
from dotenv import load_dotenv
load_dotenv()

evolution_api_key = os.getenv("EVOLUTION_API_KEY")
app = FastAPI()


async def send_message(to:str, message: str):
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
        message_text = data['data']['message']['conversation']
        await send_message(to, message_text)

    return {'hello':'world'}