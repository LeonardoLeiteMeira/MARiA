import asyncio
from typing import Any, Optional, cast
from collections.abc import Awaitable, Callable

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.tool import ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field

from domain import UserLongTermMemoryDomain
from external.notion import NotionFactory, NotionTool, NotionUserData

from ..prompts import (
    build_main_agent_prompt,
    prompt_memory_validator_node,
    prompt_route_classifier,
    prompt_simple_response_node,
)
from ..tools import (
    AskUserData,
    CreateCard,
    CreateNewMonth,
    CreateNewPlanning,
    CreateNewTransaction,
    DeleteData,
    GetCardsWithBalance,
    GetMonthData,
    GetPlanByMonth,
    ReadUserBaseData,
    RequestSaveMemory,
    SearchTransactionV2,
    ToolInterface,
    ToolType,
)
from ..tools.manage_user_memory import ManageUserMemory
from .state import State


class RouteClassifierOutput(BaseModel):
    domain: str = Field(..., description="SIMPLE, OPERACIONAL ou ANALITICO.")
    confidence: float = Field(..., ge=0.0, le=1.0)


class MariaGraph:
    def __init__(
        self,
        initial_prompt: str,
        notion_factory: NotionFactory,
        user_long_term_memory_domain: UserLongTermMemoryDomain,
    ):
        self.prompt = initial_prompt
        self.__notion_factory = notion_factory
        self.__user_long_term_memory_domain = user_long_term_memory_domain
        self.__notion_user_data: Optional[NotionUserData] = None
        self.__notion_tool: Optional[NotionTool] = None
        self.__agent_with_tools: Any = None
        self.__model_name = "openai:gpt-4.1"
        self.__classifier_model_name = "openai:gpt-4.1-mini"
        self.__memory_validator_model_name = "openai:gpt-4.1-mini"
        self.__simple_response_model_name = "openai:gpt-4.1"
        self.__route_confidence_threshold = 0.60
        self.__graph_nodes: set[str] = set()

        self.__tools_by_name: dict[str, ToolInterface] = {}
        self.__state_keys_cache_by_tool: dict[str, tuple[str, ...]] = {}

        self.__tools: list[type[ToolInterface]] = [
            AskUserData,
            RequestSaveMemory,
            # Tools do transaction agent
            CreateNewTransaction,
            SearchTransactionV2,
            # =====
            CreateCard,
            CreateNewMonth,
            CreateNewPlanning,
            GetPlanByMonth,
            DeleteData,
            ReadUserBaseData,
            GetMonthData,
            GetCardsWithBalance,
            # RedirectTransactionsAgent
        ]

    async def get_state_graph(
        self, notion_user_data: NotionUserData, notion_tool: NotionTool
    ) -> StateGraph:
        self.__notion_user_data = notion_user_data
        self.__notion_tool = notion_tool
        self.__agent_with_tools = None
        self.__tools_by_name = {}
        self.__state_keys_cache_by_tool = {}

        # transaction_agent = TransactionsAgentGraph()
        # transaction_agent.set_notion_factory(self.__notion_factory)
        # transactions_agent_graph = await transaction_agent.get_state_graph()
        # transactions_agent = transactions_agent_graph.compile()

        state_graph = StateGraph(State)

        state_graph.add_node("start_node", self.__start_message)
        state_graph.add_node(
            "load_long_term_memory_node", self.__load_long_term_memory_node
        )
        state_graph.add_node("classify_request", self.__classify_request)
        state_graph.add_node("simple_response_node", self.__simple_response_node)
        state_graph.add_node("main_maria_node", self.main_maria_node)
        state_graph.add_node("tools", self.__tool_node)
        state_graph.add_node("ask_user_interrupt", self.__ask_user_interrupt)
        state_graph.add_node("memory_validator_node", self.__memory_validator_node)
        # state_graph.add_node("transactions_agent", transactions_agent)
        self.__graph_nodes = {
            "start_node",
            "load_long_term_memory_node",
            "classify_request",
            "simple_response_node",
            "main_maria_node",
            "tools",
            "ask_user_interrupt",
            "memory_validator_node",
        }

        state_graph.add_edge(START, "start_node")
        state_graph.add_edge("start_node", "load_long_term_memory_node")
        state_graph.add_edge("load_long_term_memory_node", "classify_request")
        state_graph.add_conditional_edges(
            "classify_request",
            self.__route_after_classification,
            {
                "simple_response_node": "simple_response_node",
                "main_maria_node": "main_maria_node",
            },
        )
        state_graph.add_edge("simple_response_node", END)
        state_graph.add_edge("ask_user_interrupt", "memory_validator_node")
        state_graph.add_conditional_edges(
            "main_maria_node", self.__router, {"tools": "tools", END: END}
        )

        # state_graph.add_edge('transactions_agent', 'main_maria_node')

        return state_graph

    async def __create_agent(self, state: State) -> None:
        assert self.__notion_user_data is not None
        assert self.__notion_tool is not None
        self.__tools_by_name = {}
        self.__state_keys_cache_by_tool = {}

        notion_data_calls: dict[str, Callable[[], Awaitable[dict[str, Any]]]] = {}
        if not state.get("months"):
            notion_data_calls['months'] = self.__notion_user_data.get_user_months

        if not state.get("cards"):
            notion_data_calls['cards'] = self.__notion_user_data.get_user_cards

        if not state.get("categories"):
            notion_data_calls['categories'] = self.__notion_user_data.get_user_categories

        if not state.get("macroCategories"):
            notion_data_calls['macroCategories'] = self.__notion_user_data.get_user_macro_categories

        if notion_data_calls:
            notion_data_results: list[dict[str, Any]] = await asyncio.gather(
                *(call() for call in notion_data_calls.values())
            )

            state_dict = cast(dict[str, Any], state)
            for key, result in zip(notion_data_calls.keys(), notion_data_results):
                state_dict[key] = result


        if not state.get("transaction_types"):
            transaction_enum = self.__notion_tool.ger_transaction_types()
            state["transaction_types"] = [member.value for member in transaction_enum]

        instanciated_tools = []
        for Tool in self.__tools:
            tool_created = await Tool.instantiate_tool(state, self.__notion_tool)
            self.__tools_by_name[tool_created.name] = tool_created
            instanciated_tools.append(tool_created)

        self.__create_state_keys_cache_by_tool()
        agent = init_chat_model(self.__model_name, temperature=0.2)
        self.__agent_with_tools = agent.bind_tools(instanciated_tools)

    async def __start_message(self, state: State) -> dict[str, Any]:
        return {"messages": [state["user_input"]]}

    async def __load_long_term_memory_node(self, state: State) -> dict[str, Any]:
        if "long_term_memory" in state:
            return {}

        memory_tool = self.__create_manage_user_memory_tool(state)
        tool_result = await memory_tool.ainvoke(
            {"args": {"action": "read"}, "id": "load_long_term_memory"}
        )
        return {
            "long_term_memory": self.__extract_memory_from_tool_result(tool_result, {})
        }

    async def __classify_request(self, state: State) -> dict[str, Any]:
        route_fallback: dict[str, Any] = {
            "route_domain": "SIMPLE",
            "route_confidence": None,
            "route_decision": "fallback_simple",
        }

        try:
            classifier = init_chat_model(self.__classifier_model_name, temperature=0)
            classifier_with_structured_output = classifier.with_structured_output(
                RouteClassifierOutput
            )

            user_input = state.get("user_input")
            if user_input is None:
                return route_fallback

            result = await classifier_with_structured_output.ainvoke(
                [SystemMessage(prompt_route_classifier), user_input]
            )

            result = cast(RouteClassifierOutput, result)

            domain = str(result.domain).strip().upper()
            confidence = float(result.confidence)

            if domain not in {"SIMPLE", "OPERACIONAL", "ANALITICO"} or confidence < self.__route_confidence_threshold:
                return {
                    "route_domain": "SIMPLE",
                    "route_confidence": confidence,
                    "route_decision": "fallback_simple",
                }

            return {
                "route_domain": domain,
                "route_confidence": confidence,
                "route_decision": "classified",
            }
        except Exception:
            return route_fallback

    def __route_after_classification(self, state: State) -> str:
        route_domain = str(state.get("route_domain", "SIMPLE")).upper()
        if route_domain == "SIMPLE":
            return "simple_response_node"
        if route_domain in {"OPERACIONAL", "ANALITICO"}:
            return "main_maria_node"
        return "simple_response_node"

    async def __simple_response_node(self, state: State) -> dict[str, Any]:
        messages = state.get("messages", [])
        simple_model = init_chat_model(self.__simple_response_model_name, temperature=0.2)
        chain_output = await simple_model.ainvoke(
            [SystemMessage(prompt_simple_response_node), *messages]
        )
        return {**state, "messages": [chain_output]}

    async def main_maria_node(self, state: State) -> dict[str, Any]:
        """Node with chatbot logic"""
        messages = state.get("messages", [])
        if self.__agent_with_tools is None:
            await self.__create_agent(state)
        prompt = build_main_agent_prompt(self.prompt, state.get("long_term_memory"))
        chain_output = await self.__agent_with_tools.ainvoke(
            [SystemMessage(prompt), *messages]
        )
        return {**state, "messages": [chain_output]}

    def __router(self, state: State) -> str:
        if messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    async def __tool_node(self, state: State) -> Command[str]:
        if messages := state.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs: list[ToolMessage] = []
        state_updates: dict[str, Any] = {}
        pending_memory_intent_description: str | None = None
        pending_memory_tool_call_id: str | None = None

        for tool_call in message.tool_calls:
            try:
                tool_to_call = self.__tools_by_name.get(tool_call["name"])

                if tool_to_call is None:
                    outputs.append(
                        ToolMessage(
                            content=f"TOOL {tool_call['name']} NOT FOUND",
                            tool_call_id=tool_call["id"],
                        )
                    )
                    continue

                tool_type = tool_to_call.tool_type
                if tool_type == ToolType.HUMAN_INTERRUPT:
                    question = self.__extract_interrupt_question(tool_call.get("args"))
                    return Command(
                        goto="ask_user_interrupt",
                        update={
                            "messages": [
                                *outputs,
                                ToolMessage(
                                    content=f"Pergunta ao usuário: {question}",
                                    tool_call_id=tool_call["id"],
                                )
                            ],
                            "pending_interrupt_question": question,
                            "pending_interrupt_tool_call_id": tool_call["id"],
                        },
                    )
                if tool_type == ToolType.AGENT_REDIRECT:
                    handoff_target = tool_call["name"]
                    if handoff_target not in self.__graph_nodes:
                        outputs.append(
                            ToolMessage(
                                content=f"HANDOFF TARGET {handoff_target} NOT REGISTERED",
                                tool_call_id=tool_call["id"],
                            )
                        )
                        continue
                    return Command(
                        goto=handoff_target,
                        update={
                            "messages": [
                                *outputs,
                                ToolMessage(
                                    content=f"Transferido para {handoff_target}",
                                    tool_call_id=tool_call["id"],
                                )
                            ],
                            "args": tool_call["args"],
                        },
                    )
                if tool_type == ToolType.MEMORY_SIGNAL:
                    pending_memory_intent_description = str(
                        tool_call.get("args", {}).get("description", "")
                    )
                    pending_memory_tool_call_id = tool_call["id"]
                    continue

                tool_result = await tool_to_call.ainvoke(
                    {"args": tool_call["args"], "id": tool_call["id"]}
                )
                outputs.append(tool_result)
                state_updates.update(
                    self.__invalidate_state_cache(state, tool_to_call.name)
                )
            except Exception as e:
                outputs.append(
                    ToolMessage(
                        content=f"ERROR TO EXECUTE TOOL: {tool_call['name']}. ERROR: {str(e)}",
                        tool_call_id=tool_call["id"],
                    )
                )

        updates: dict[str, Any] = {**state_updates}
        if outputs:
            updates["messages"] = outputs

        if pending_memory_intent_description and pending_memory_tool_call_id:
            updates["pending_memory_intent_description"] = pending_memory_intent_description
            updates["pending_memory_tool_call_id"] = pending_memory_tool_call_id
            return Command(
                goto="memory_validator_node",
                update=updates,
            )

        return Command(
            goto="main_maria_node",
            update=updates,
        )

    async def __ask_user_interrupt(self, state: State) -> dict[str, Any]:
        question = state.get("pending_interrupt_question")
        if not question:
            raise ValueError("No pending interrupt question found in state.")

        payload: dict[str, Any] = {"question": question}
        if tool_call_id := state.get("pending_interrupt_tool_call_id"):
            payload["tool_call_id"] = tool_call_id

        user_response = interrupt(payload)
        return {
            "messages": [HumanMessage(str(user_response))],
            "pending_interrupt_question": None,
            "pending_interrupt_tool_call_id": None,
            "question_from_interrupt": payload["question"],
            "answer_from_interrupt": user_response
        }

    async def __memory_validator_node(self, state: State) -> Command[str]:
        memory_input = self.__build_memory_validator_input(state)
        memory_update: dict[str, Any] = {
            "pending_memory_intent_description": None,
            "pending_memory_tool_call_id": None,
        }

        if memory_input is None:
            return self.__build_memory_validator_command(state, memory_update)

        memory_tool = self.__create_manage_user_memory_tool(state)
        memory_agent = init_chat_model(
            self.__memory_validator_model_name,
            temperature=0,
        ).bind_tools([memory_tool])

        chain_output = await memory_agent.ainvoke(
            [
                SystemMessage(self.__build_memory_validator_prompt(state)),
                HumanMessage(memory_input),
            ]
        )

        current_memory = dict(state.get("long_term_memory", {}))
        if hasattr(chain_output, "tool_calls"):
            for tool_call in chain_output.tool_calls:
                if tool_call["name"] != memory_tool.name:
                    continue

                tool_result = await memory_tool.ainvoke(
                    {"args": tool_call["args"], "id": tool_call["id"]}
                )
                current_memory = self.__extract_memory_from_tool_result(
                    tool_result, current_memory
                )

        memory_update["long_term_memory"] = current_memory
        return self.__build_memory_validator_command(state, memory_update)

    def __extract_interrupt_question(self, tool_args: Any) -> str:
        # TODO verificar o tipo certo para evitar esses ifs
        if isinstance(tool_args, dict):
            if question := tool_args.get("question"):
                return str(question)
            if query := tool_args.get("query"):
                return str(query)
        if isinstance(tool_args, str):
            return tool_args
        return "Pode detalhar melhor os dados que faltam para continuar?"

    def __build_memory_validator_command(
        self, state: State, update: dict[str, Any]
    ) -> Command[str]:
        if pending_memory_tool_call_id := state.get("pending_memory_tool_call_id"):
            update["messages"] = [
                ToolMessage(
                    content="Memory intent evaluated.",
                    tool_call_id=pending_memory_tool_call_id,
                )
            ]
        return Command(goto="main_maria_node", update=update)

    def __build_memory_validator_input(self, state: State) -> str | None:
        if pending_memory_intent_description := state.get(
            "pending_memory_intent_description"
        ):
            return pending_memory_intent_description
        
        if question_interrupt := state.get(
            "question_from_interrupt"
        ):
            answer = state.get("answer_from_interrupt", "")
            return f"Question made: '{question_interrupt}'. Answer from user: '{answer}'"

        return None

    def __build_memory_validator_prompt(self, state: State) -> str:
        current_memory = state.get("long_term_memory", {})
        if not current_memory:
            memory_section = "Memória atual do usuário:\n- Nenhuma memória salva."
        else:
            rendered_memory = "\n".join(
                f"- {key}: {value}"
                for key, value in sorted(current_memory.items(), key=lambda item: item[0])
            )
            memory_section = f"Memória atual do usuário:\n{rendered_memory}"

        return f"{prompt_memory_validator_node.strip()}\n\n{memory_section}"

    def __create_manage_user_memory_tool(self, state: State) -> ManageUserMemory:
        return ManageUserMemory(state, self.__user_long_term_memory_domain)

    def __extract_memory_from_tool_result(
        self,
        tool_result: ToolMessage,
        fallback: dict[str, str],
    ) -> dict[str, str]:
        artifact = getattr(tool_result, "artifact", None)
        if not isinstance(artifact, dict):
            return dict(fallback)

        normalized_memory: dict[str, str] = {}
        for key, value in artifact.items():
            normalized_memory[str(key)] = str(value)
        return normalized_memory

    def __invalidate_state_cache(self, state: State, tool_name: str) -> dict[str, None]:
        keys_to_reset = self.__state_keys_cache_by_tool.get(tool_name)
        if not keys_to_reset:
            return {}
        updates: dict[str, None] = {}
        state_dict = cast(dict[str, Any], state)
        for key in keys_to_reset:
            if key in state_dict:
                state_dict[key] = None
                updates[key] = None
        return updates

    def __create_state_keys_cache_by_tool(self) -> None:
        for tool in self.__tools_by_name.values():
            if isinstance(tool, CreateCard):
                self.__state_keys_cache_by_tool[tool.name] = ("cards",)
            if isinstance(tool, CreateNewMonth):
                self.__state_keys_cache_by_tool[tool.name] = ("months",)
            if isinstance(tool, DeleteData):
                self.__state_keys_cache_by_tool[tool.name] = (
                    "cards",
                    "categories",
                    "macroCategories",
                    "months",
                )
