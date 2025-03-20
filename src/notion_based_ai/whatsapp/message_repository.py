import asyncio
import asyncpg
from dotenv import load_dotenv
import os
from datetime import datetime
import json
load_dotenv()

class MessageRepository:
    def __init__(self):
        self.user = os.getenv('POSTGRES_USER')
        self.password = os.getenv('POSTGRES_PASSWORD')
        
    def _get_message_from_message_dict(self, message_dict: dict):
        if 'conversation' in message_dict:
            return message_dict['conversation']
        else:
            return next(iter(message_dict))

    async def get_last_messages(self, remoteJid: str):
        try:
            conn = await asyncpg.connect(
                user=self.user,
                password=self.password, 
                database='usuario',
                host='localhost'
            )

            query = f'SELECT * FROM "Message" WHERE "key" ->>\'remoteJid\' = \'{remoteJid}\' ORDER BY "messageTimestamp" DESC LIMIT 10;'
            rows = await conn.fetch(query)
            
            results = [dict(row) for row in rows]
            
            messages = []
            for message_record in results:
                key_dict = json.loads(message_record['key'])
                message_dict = json.loads(message_record['message'])
                
                formatted_message = {
                    'is_from_ai': key_dict['fromMe'],
                    'sender_name': message_record['pushName'],
                    'message_text': self._get_message_from_message_dict(message_dict),
                    'timestamp': datetime.fromtimestamp(message_record['messageTimestamp'])
                }
                messages.append(formatted_message)

            return messages

        except Exception as e:
            print("Ocorreu o seguinte erro: ", e)
            return []
        finally:
            print("Fechando conexão...")
            await conn.close()

