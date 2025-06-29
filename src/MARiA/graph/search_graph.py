# import json
# from typing import Literal
# from langgraph.graph import StateGraph, END
# from langgraph.types import Command
# from langchain_core.messages import SystemMessage, HumanMessage
# from MARiA.agents import create_maria_agent, maria_read_access, maria_write_access
# from MARiA.notion_repository import notion_access
# from external.enum.enums import NotionDatabaseEnum
# # from external import EjFinanceAccess
# # from MARiA.notion_types import NotionDatabaseEnum
# from pydantic import create_model

# from typing import Annotated
# from langgraph.graph.message import add_messages
# from typing_extensions import TypedDict
# from langchain_core.messages import HumanMessage

# from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent

# class SearchState(TypedDict):
#     messages: Annotated[list, add_messages]
#     search_input: str
#     table_name: str
#     table_structure: dict
#     table_relations: dict
#     columns_to_search: list


# def maria_read_access(): #-> CompiledGraph:
#     prompt = " "
#     model = ChatOpenAI(model='gpt-4o-mini', temperature=0)
#     tools = []
#     model = model.bind_tools(tools)
#     agent = create_react_agent(
#         model,
#         tools=tools,
#         prompt=prompt,
#         debug=True
#     )
#     return agent


# identify_table_prompt = f"""
# Você tem a função de escolher qual tabela certa satisfaz a busca do usuário. 
# Por exemplo: 
# Para a solicitação 'Quero ver todas as transações da nubank', a respostam deve ser a tabela de transações. 
# Outro exemplo: Solicitação 'Quero saber quanto gastei esse mes' a resposta deve ser a tabela de meses, onde cada mes tem os dados calculados.

# Breve descrição das tabelas: 
# """

# #TODO melhorar esse prompt pois nao esta pegando as colunas corretamente
# identify_columns_relations_prompt = f"""
# Dada uma determinada busca em linguagem natural e uma lista de tabelas externas, sua função é identificar quais dessas tabelas externas são relevantes para aquela busca.

# Exemplo 1:
# Tabela alvo: Transactions
# Tabelas relacionadas: [Categorias, Entrada em, Saida de, Macro Categoria, Gestão]
# Busca do usuário: 'Transações do mes de maio de de 2025 da categoria transporte.'

# Resultado esperado: [Categorias, Gestão]
# Justificativa: Na listagem de tabelas relacionadas, 'Categorias' é relacionada a categoria transporte, e 'Gestão' é relacionada ao filtro do mês de maio.

# Exemplo 2:
# Tabela alvo: Transactions
# Tabelas relacionadas: [Categorias, Entrada em, Saida de, Macro Categoria, Gestão]
# Busca do usuário: 'Transações do mes de abril de de 2025, essenciais e feitas no cartao da nubank.'

# Resultado esperado: [Macro Categorias, Entrada em, Saida de, Gestão]
# Justificativa: 'Macro Categorias' se refere a classificação 'essencial' da busca, 'Entrada em' e 'Saida de' são campos que podem ter o cartão nubank da busca, e 'Gestão' se refere ao mes de abril da busca.


# Analise a seguinte busca e a estrutura da tabela, e então retorne a lista de tabelas relacionadas relevantes para esssa busca. Na duvida sobre uma coluna, retorne ela, pois é melhor errar para mais do que para menos!


# Tabela alvo: <TABLE>
# Tabelas relacionadas: <RALATIONS>
# Busca do usuário: <SEARCH>

# Retorne o resultado esperado.
# """

# class SearchGraph:
#     def __init__(self):
#         self.model = "gpt-4o-mini"
#         self.notion_access = notion_access
#         self.prompt = identify_table_prompt
#         databases = [member.value for member in NotionDatabaseEnum]
#         self.database_structures = {}
#         for database in databases:
#             properties = self.notion_access.get_properties(database)
#             self.database_structures[database] = properties
#             properties_formated = ", ".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in properties.items())
#             self.prompt += f"\n{database}: {properties_formated}"

#     def __dict_to_string(self, data: dict):
#         return ", ".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in data.items())
    
#     def __list_property_to_string(self, list_property: list[dict]):
#         return ", ".join(f"{property['name']}: {json.dumps(property, ensure_ascii=False)}" for property in list_property)
    
#     def build_graph(self) -> StateGraph:
#         pass


#     async def table_structure_node(self, state: SearchState):
#         schema = {
#             "title": "TableSelection",
#             "description": 'Selecionar uma tabela que resolva a solicitação',
#             "type": "object",
#             "properties": {
#                 "table_name": {
#                     "type": "string",
#                     "enum": [member.value for member in NotionDatabaseEnum]
#                 },
#                 "table_sctructure": {
#                     "type": "string"
#                 }
#             },
#             "required": ["table_name", "table_sctructure"]
#         }

#         llm = ChatOpenAI(model=self.model, temperature=0)
#         choose_table = llm.with_structured_output(schema)

#         input = state['search_input']

#         prompt = f"{self.prompt}\n\nBusca: {input}"

#         result = await choose_table.ainvoke(prompt)
#         state['table_name'] = result['table_name']

#         full_structure = self.database_structures[result['table_name']]
#         state['table_structure'] = self.__dict_to_string(full_structure)

#         relation_properties = [value for key, value in full_structure.items() if value['type'] == 'relation']
#         state['table_relations'] = self.__list_property_to_string(relation_properties)
#         return state
    
#     async def relations_node(self, state: SearchState):
#         schema = {
#             "title": "ColumnsAndRelations",
#             "description": 'Selecionar as colunas envolvidas na busca e as colunas da busca do tipo relation',
#             "type": "object",
#             "properties": {
#                 "columns": {
#                     "type": "array",
#                     "items": {
#                         "type": "string"
#                     },
#                     "description": "Lista de colunas relevantes para a busca"
#                 }
#             },
#             "required": ["columns"]
#         }

#         llm = ChatOpenAI(model=self.model, temperature=0)
#         select_columns = llm.with_structured_output(schema)

#         table = state["table_name"]
#         relations = state["table_relations"]
#         search = state["search_input"]

#         final_propmpt = identify_columns_relations_prompt.replace(
#             "<TABLE>", table
#             ).replace("<RALATIONS>", relations
#             ).replace('<SEARCH>', search)
        
#         result = await select_columns.ainvoke(final_propmpt)
#         print(result['columns'])
#         state["columns_to_search"] = result['columns']
#         return state
    


#     # TODO dado a busca e a estutrutura definir quais colunas do tipo relation soa relevantes para a busca
#     # Por exemplo, se a busca tiver a filtragem por mes, preciso achar o mes na tabela de mes
#     # Se tiver um cartao, preciso achar ele na tabela de cartoes
#     # Mesma coisa para categorias
#     async def get_relations_id(self):
#         pass

#     #TODO Usar a tabela e o schema para montar a query
#     async def build_query_and_run(self):
#         pass



    


# if __name__ == "__main__":
#     import asyncio

#     async def testSelectTable():
#         try:
#             graph = SearchGraph()
#             state = SearchState()
#             tests = [
#                 ("Transacoes do mes de maio", "transactions"),
#                 ("Transacoes do mes atual, que sao essenciais, e da categoria transporte", 'transactions'),
#                 ("Valor total de gasto do mes atual", "months"),
#                 ("Planejamento do mes passado", 'planning'),
#                 ("Mes com maior valor de entrada do ano", 'months'),
#                 ("Mes em que foi planejado o maior gasto do ano", 'months'),
#                 ("Buscar a conta com maior saldo", 'cards'),
#                 ("Buscar o cartao que esta mais devendo", 'cards'),
#             ]

#             for test in tests:
#                 input = test[0]
#                 expected = test[1]
#                 state['search_input'] = input
#                 state = await graph.table_structure_node(state)

#                 await graph.relations_node(state)


#             print("+++++++++++++++++++++++++++++++++")
#         except Exception as e:
#             print("ERROR: ", e)
    
#     async def testSelectColumns():
#         try:
#             graph = SearchGraph()
#             state = SearchState()
#             properties = graph.database_structures['transactions']

#             state["table_name"] = 'transactions'
#             state["search_input"] = 'Transacoes do mes de maio'
#             state["table_structure"] =  ", ".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in properties.items())

#             relation_properties = [value for key, value in properties.items() if value['type'] == 'relation']
#             state['table_relations'] = ", ".join(f"{property['name']}: {json.dumps(property, ensure_ascii=False)}" for property in relation_properties)

#             await graph.relations_node(state)
#         except Exception as e:
#             print("Error: ", e)
            
    
#     asyncio.run(testSelectTable())

