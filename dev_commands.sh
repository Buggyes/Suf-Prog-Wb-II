#source bin/activate
#deactivate
#uvicorn main:app --reload

# example test request:
#curl -X POST http://localhost:8000/users/ \
#  -H "Content-Type: application/json" \
#  -d '{"login": "john_doe", "password": "secret123"}'
