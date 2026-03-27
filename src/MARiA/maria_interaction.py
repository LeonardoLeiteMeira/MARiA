from contextlib import _AsyncGeneratorContextManager
from typing import Any, cast
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from datetime import datetime
from langchain_core.runnables import RunnableConfig

from .graph import MariaGraph
from domain import UserDomain
from repository import UserModel, ThreadModel
from external.notion import NotionFactory, NotionUserData, NotionTool


class MariaInteraction:
    def __init__(
        self,
        user_domain: UserDomain,
        maria_graph: MariaGraph,
        checkpointer_manager: _AsyncGeneratorContextManager[AsyncPostgresSaver],
    ):
        self.__user_domain = user_domain
        self.__checkpointer = checkpointer_manager
        self.__maria_graph = maria_graph

    async def get_maria_answer(self, user: UserModel, user_input: str) -> str:
        current_thread = await self.__get_current_thread(cast(str, user.id))
        thread_id_str = str(current_thread.id)
        config: RunnableConfig = {"configurable": {"thread_id": thread_id_str}}
        now = datetime.now()
        current_time = now.strftime("%I:%M %p, %B %d, %Y")
        user_input_with_name = f"{current_time} - {user.name}: {user_input}"

        async with self.__checkpointer as checkpointer:
            await checkpointer.setup()
            notion_user_data, notion_tool = self.__get_notion_instances(user)
            state_graph = await self.__maria_graph.get_state_graph(
                notion_user_data, notion_tool
            )

            compiled = state_graph.compile(checkpointer=checkpointer)
            snapshot = await compiled.aget_state(config, subgraphs=True)
            interrupts = self.__collect_interrupts(snapshot)

            if interrupts:
                cmd: Command[Any] = Command(resume=user_input_with_name)
                result = await compiled.ainvoke(cmd, config=config, debug=True)
            else:
                result = await compiled.ainvoke(
                    {
                        "user_input": HumanMessage(user_input_with_name),
                        "user_id": str(user.id),
                    },
                    config=config,
                    debug=True,
                )

            post_invoke_snapshot = await compiled.aget_state(config, subgraphs=True)
            pending_interrupts = self.__collect_interrupts(post_invoke_snapshot)
            if question := self.__extract_interrupt_question(pending_interrupts):
                return question

            if not isinstance(result, dict):
                raise ValueError("Invalid graph result type.")

            messages = result.get("messages", [])
            if not messages:
                raise ValueError("No messages found in graph result.")

            resp = cast(str, messages[-1].content)
            return resp

    async def __get_current_thread(self, user_id: str) -> ThreadModel:
        user_threads = await self.__user_domain.get_user_valid_thread(user_id)
        if len(user_threads) < 1:
            current_thread = await self.__user_domain.create_new_user_thread(user_id)
        else:
            current_thread = user_threads[0]
        return current_thread

    def __get_notion_instances(
        self, user: UserModel
    ) -> tuple[NotionUserData, NotionTool]:
        notion_factory = NotionFactory()
        notion_factory.set_user_access_token(user.notion_authorization.access_token)
        notion_factory.set_user_datasources(user.notion_datasources)

        notion_user_data = notion_factory.create_notion_user_data()
        notion_tool = notion_factory.create_notion_tool()

        return (notion_user_data, notion_tool)

    def __collect_interrupts(self, snapshot: Any) -> tuple[Any, ...]:
        if snapshot_interrupts := getattr(snapshot, "interrupts", None):
            return tuple(snapshot_interrupts)
        return tuple(
            intr
            for task in getattr(snapshot, "tasks", ())
            for intr in getattr(task, "interrupts", ())
        )

    def __extract_interrupt_question(self, interrupts: tuple[Any, ...]) -> str | None:
        if not interrupts:
            return None
        payload = getattr(interrupts[0], "value", None)
        # TODO verificar o tipo certo para evitar esses ifs
        if isinstance(payload, dict):
            if question := payload.get("question"):
                return str(question)
            if query := payload.get("query"):
                return str(query)
        if isinstance(payload, str):
            return payload
        return None
