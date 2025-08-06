##Caso o ambiente virtual do python não inicialize automaticamente
#source bin/activate
#deactivate
#uvicorn main:app --root-path RestAPIFurb --reload

## Exemplo de requisição:
#curl -X POST http://localhost:8000/endpoint/ \
#  -H "Content-Type: application/json" \
#  -d '{"login": "usuario", "password": "senha123"}'
