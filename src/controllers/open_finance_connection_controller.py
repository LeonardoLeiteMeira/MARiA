from collections.abc import Callable

from fastapi import APIRouter, Request, Depends, Body

from external.pluggy import PluggyAuthLoader
from repository import PluggyItemModel
from application import OpenFinanceApplication

class OpenFinanceConnectionController(APIRouter):
    def __init__(self, jwt_dependency: Callable, pluggy_auth_dependency: Callable, open_finance_app: Callable):
        super().__init__(
            prefix='/open-finance',
            dependencies=[Depends(jwt_dependency)]
        )

        @self.post("/connect-token")
        async def get_connect_token(request: Request, pluggy_auth_loader: PluggyAuthLoader = Depends(pluggy_auth_dependency)) -> dict[str, str]:
            user = request.state.user
            connect_token = await pluggy_auth_loader.get_connect_token(
                webhook_url="https://maria_pluggy_test.requestcatcher.com/pluggy",
                client_user_id=str(user.id)
            )
            return connect_token
            
        @self.post("/webhook")
        async def webhook():
            pass

        @self.post("/item-from-widget")
        async def receive_item_from_widget(request: Request, item_data: dict = Body(...), open_finance_app:OpenFinanceApplication = Depends(open_finance_app)):
            user = request.state.user
            pluggy_item = PluggyItemModel.from_request_body(item_data, str(user.id))
            await open_finance_app.create_new_item(pluggy_item)
        


