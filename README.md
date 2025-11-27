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


## Project management
The project management can be accessed in this [notion](https://leonardoleite.notion.site/MARiA-2b614f691c8380298eecfec9c2cbb3d7?source=copy_link)


# Alembic
- poetry run alembic init -t async alembic
- poetry run alembic revision -m "create_table_users"
- poetry run alembic upgrade head
- poetry run alembic downgrade -1

# Access database in productioin

docker compose exec -e PGPASSWORD='passwordHere' containerName psql -U user


