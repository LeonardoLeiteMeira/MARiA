from typing import Any, cast

import httpx


class PluggyAuthLoader:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.__client_id = client_id
        self.__client_secret = client_secret

    async def get_api_key(self) -> str | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.pluggy.ai/auth",
                    json={
                        "clientId": self.__client_id,
                        "clientSecret": self.__client_secret,
                    },
                    headers={
                        "accept": "application/json",
                        "content-type": "application/json",
                    },
                )
                resp_json = response.json()
                token = cast(str, resp_json["apiKey"])
                return token
        except Exception as e:
            print("Error to get api key", e)
        return None

    async def get_connect_token(
        self,
        webhook_url: str | None = None,
        oauth_redirect_uri: str | None = None,
        avoid_duplicates: bool = False,
        client_user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Options to het connect token
        - clientUserId : Provide this value for end-to-end traceability of your user's connection, you can send any reference for the user that you want to use, and it will be available for each item created on the Pluggy Connect Widget, that used this
        connectToken
        - webhookUrl: When providing this value, it works the same way as creating an item with webhookUrl parameter. It will send all item events to that URL, besides the other webhooks configured at the client level.
        - oauthRedirectUri: Url to redirect the user after the connect flow.
        - avoidDuplicates: Avoids creating a new item if there is already one with the same credentials.
        """
        api_key = await self.get_api_key()
        try:
            async with httpx.AsyncClient() as client:
                json_body: dict[str, Any] = {}

                if webhook_url is not None:
                    json_body["webhookUrl"] = webhook_url

                if webhook_url is not None:
                    json_body["oauthRedirectUri"] = oauth_redirect_uri

                if webhook_url is not None:
                    json_body["avoidDuplicates"] = avoid_duplicates

                if webhook_url is not None:
                    json_body["clientUserId"] = client_user_id

                response = await client.post(
                    "https://api.pluggy.ai/connect_token",
                    headers={
                        "X-API-KEY": cast(str, api_key),
                        "accept": "application/json",
                        "content-type": "application/json",
                    },
                    json=json_body,
                )
                resp_json = response.json()
                return cast(dict[str, Any], resp_json)
        except Exception as e:
            print("Error to get connect token", e)
        return None
