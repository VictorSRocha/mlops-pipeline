
"""Servidor fake para simular a API de clientes com erros propositais."""
import random
import uvicorn
from fastapi import FastAPI, HTTPException, Header

app = FastAPI(title="Fake Streaming API")

# Gera dados sinteticos uma vez ao subir o servidor
random.seed(42)
TOTAL_CUSTOMERS = 1500
PLANS = ["basic", "standard", "premium"]
REGIONS = ["SP", "RJ", "MG", "RS", "PR"]

FAKE_TOKEN = "token-de-teste"

ALL_CUSTOMERS = [
    {
        "customer_id": f"C{i:04d}",
        "plan": random.choice(PLANS),
        "region": random.choice(REGIONS),
        "age": random.randint(18, 70),
        "churned": random.randint(0, 1),
        "signup_date": f"202{random.randint(5,6)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    }
    for i in range(1, TOTAL_CUSTOMERS + 1)
]

def _maybe_fail():
    """Injeta erros aleatorios para demonstrar o retry em acao."""
    rng = random.random()
    if rng < 0.30:   # 30% de chance de HTTP 500
        raise HTTPException(status_code=500, detail="Erro simulado!")
    if rng < 0.40:   # 10% de chance de HTTP 429
        raise HTTPException(status_code=429, detail="Rate limit!")

def _valida_token(authorization):
    """Verifica se o token passado pelo usuário é um token válido"""
    token = authorization.replace("Bearer ", "")
    if token != FAKE_TOKEN:
        raise HTTPException(status_code=401, detail="Token invalido")

@app.get("/v1/customers")
def get_customers(
    page: int = 1,
    page_size: int = 100,
    authorization: str = Header(default=None),
):
    # Valida o token
    _valida_token(authorization)

    # Injeta erros aleatorios
    _maybe_fail()

    # Paginacao
    start = (page - 1) * page_size
    end = start + page_size
    items = ALL_CUSTOMERS[start:end]
    return {
        "items": items,
        "page": page,
        "has_next": end < len(ALL_CUSTOMERS),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
