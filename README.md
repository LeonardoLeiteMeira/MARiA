# Finance AI assist

I'm building an AI assist to help me with my financial organizations. 
This AI agent, called MARiA, access my personal notion workspace and read my financial page to answer some questions and help me understand my expenses.
She can create new transactions and read diferents notion databases.

# Technical details
- I'm usuing poetry to manage packages
- Lanchchain to create the agent
- Notion to store data (for now), and API to access
- FastAPI to create an API - To use the agent with other applications
- ... 


## To do List
- [x] Fazer query de planejamento
- [x] Modificar busca dos dados: Ao busca categorias não esta listando todas pois esta limitado em 10. Devo mexer para que a AI saiba disso e possa buscar mais (mas deixar mais de 10 o default pode ser uma boa)
- [ ] Fazer queries em transações
- [ ] Conectar no whatsapp
- [ ] Lista todas as funcoes e testes que quero levar para o web summit
- [ ] Update de informação (se conseguir antes do web summit seria top)
- [ ] Fazer um planejamento (Multi agente?)



## To Do Future 
Pesquisar sobre e implementar uma cache no redis para as chamadas de tools. Dessa forma evitando chamadas desnecessárias e demoradas nas APIs utilizadas
