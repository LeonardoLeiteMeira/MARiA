import httpx
import dotenv
import os

dotenv.load_dotenv()

async def get_api_key() -> str:
    try:
        async with httpx.AsyncClient() as client:
            client_id = os.getenv("PLUGGY_CLIENT_ID")
            client_secret = os.getenv("PLUGGY_CLIENT_SECRET")

            response = await client.post(
                "https://api.pluggy.ai/auth",
                json={"clientId": client_id, "clientSecret": client_secret},
                headers={
                    "accept": "application/json",
                    "content-type": "application/json"
                },
            )
            resp_json = response.json()
            token = resp_json["apiKey"]
            return token
    except Exception as e:
        print(e)


async def get_connect_token(webhook_url: str = None, oauth_redirect_uri: str = None, avoid_duplicates: bool = False, client_user_id: str = None) -> dict:
    """
    Options to het connect token
    - clientUserId : Provide this value for end-to-end traceability of your user's connection, you can send any reference for the user that you want to use, and it will be available for each item created on the Pluggy Connect Widget, that used this
    connectToken
    - webhookUrl: When providing this value, it works the same way as creating an item with webhookUrl parameter. It will send all item events to that URL, besides the other webhooks configured at the client level.
    - oauthRedirectUri: Url to redirect the user after the connect flow.
    - avoidDuplicates: Avoids creating a new item if there is already one with the same credentials.
    """
    api_key = await get_api_key()
    async with httpx.AsyncClient() as client:
        json_body = {}

        if webhook_url != None:
            json_body['webhookUrl'] = webhook_url

        if webhook_url != None:
            json_body['oauthRedirectUri'] = oauth_redirect_uri

        if webhook_url != None:
            json_body['avoidDuplicates'] = avoid_duplicates

        if webhook_url != None:
            json_body['clientUserId'] = client_user_id

        response = await client.post(
            "https://api.pluggy.ai/connect_token",
            headers={
                "X-API-KEY": api_key,
                "accept": "application/json",
                "content-type": "application/json"
            },
            json=json_body
        )
        resp_json = response.json()
        return resp_json

