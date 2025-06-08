from messaging import MessageService
from typing import Callable
from .custom_state import CustomState

def create_message_service(appState: CustomState) -> Callable[[], MessageService]:
    evo_instance = 'maria'
    def dependency() -> MessageService:
        return MessageService(appState.database, appState.graph, evo_instance)

    return dependency