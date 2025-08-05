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
        async def receive_item_from_widget(item_data: dict = Body(...), open_finance_app:OpenFinanceApplication = Depends(open_finance_app)):
            pluggy_item = PluggyItemModel.from_request_body(item_data)
            await open_finance_app.create_new_item(pluggy_item)

#         {
#     "item": {
#         "id": "290b6757-72e9-44bf-8fe9-60e09a6a833a",
#         "connector": {
#             "id": 2,
#             "name": "Pluggy Bank",
#             "primaryColor": "ef294b",
#             "institutionUrl": "https://pluggy.ai",
#             "country": "BR",
#             "type": "PERSONAL_BANK",
#             "credentials": [
#                 {
#                     "label": "User",
#                     "name": "user",
#                     "type": "text",
#                     "placeholder": "",
#                     "validation": "^user-.{2,50}$",
#                     "validationMessage": "O user deve começar com \"user-\"",
#                     "optional": false
#                 },
#                 {
#                     "label": "Password",
#                     "name": "password",
#                     "type": "password",
#                     "placeholder": "",
#                     "validation": "^.{6,20}$",
#                     "validationMessage": "A senha deve ter entre 6 e 20 caracteres",
#                     "optional": false
#                 }
#             ],
#             "imageUrl": "https://cdn.pluggy.ai/assets/connector-icons/sandbox.svg",
#             "hasMFA": false,
#             "health": {
#                 "status": "ONLINE",
#                 "stage": null
#             },
#             "products": [
#                 "ACCOUNTS",
#                 "CREDIT_CARDS",
#                 "TRANSACTIONS",
#                 "PAYMENT_DATA",
#                 "INVESTMENTS",
#                 "INVESTMENTS_TRANSACTIONS",
#                 "IDENTITY",
#                 "LOANS"
#             ],
#             "createdAt": "2020-09-07T00:08:06.588Z",
#             "isSandbox": true,
#             "isOpenFinance": false,
#             "updatedAt": "2025-08-03T20:07:20.291Z",
#             "supportsPaymentInitiation": false,
#             "supportsScheduledPayments": false,
#             "supportsSmartTransfers": false,
#             "supportsBoletoManagement": false
#         },
#         "createdAt": "2025-08-03T20:19:45.889Z",
#         "updatedAt": "2025-08-03T20:20:07.918Z",
#         "status": "UPDATED",
#         "executionStatus": "SUCCESS",
#         "lastUpdatedAt": "2025-08-03T20:20:07.854Z",
#         "webhookUrl": null,
#         "error": null,
#         "clientUserId": null,
#         "consecutiveFailedLoginAttempts": 0,
#         "statusDetail": null,
#         "parameter": null,
#         "userAction": null,
#         "nextAutoSyncAt": null,
#         "autoSyncDisabledAt": null,
#         "consentExpiresAt": null,
#         "products": [
#             "ACCOUNTS",
#             "CREDIT_CARDS",
#             "TRANSACTIONS"
#         ],
#         "oauthRedirectUri": null
#     }
# }
        


