"""
fake_api_server.py
──────────────────
Servidor HTTP local que simula a API de clientes de streaming usada no Ep 01
da Trilha MLOps. Serve como substituto real durante a gravação — o collect_api.py
faz chamadas HTTP verdadeiras para localhost:8000 sem saber que é um simulador.

Localização no projeto:
    mlops-pipeline/
    └── scripts/
        └── fake_api_server.py   ← AQUI

Como usar:
    # Terminal 1 — sobe o servidor
    pip install fastapi uvicorn
    python scripts/fake_api_server.py

    # Terminal 2 — configura o .env para apontar para localhost
    # API_BASE_URL=http://127.0.0.1:8000/v1
    # API_TOKEN=token-de-teste

    # Terminal 2 — roda a coleta normalmente (sem nenhuma alteração no collect_api.py)
    python -m src.data.pipeline

Comportamentos simulados propositalmente para o episódio:
    - Paginação real com has_next e total
    - Autenticação por Bearer Token (401 se inválido)
    - Erros 500 aleatórios (30% das requisições) → demonstra o retry ao vivo
    - Erros 429 Rate Limit (10% das requisições) → demonstra backoff exponencial
    - Log de cada requisição no terminal do servidor → viewer vê o que acontece
"""

import logging
import os
import random
import time
from typing import Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse

# ── Configuração de logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] FAKE-API — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Constantes configuráveis via variável de ambiente ─────────────────────
VALID_TOKEN = os.getenv("FAKE_API_TOKEN", "token-de-teste")
"""Bearer token aceito pelo servidor. Altere via FAKE_API_TOKEN no .env."""

TOTAL_CUSTOMERS = int(os.getenv("FAKE_API_TOTAL", "1500"))
"""Quantidade total de clientes sintéticos gerados na inicialização."""

ERROR_500_RATE = float(os.getenv("FAKE_API_ERROR_500", "0.30"))
"""Probabilidade (0–1) de retornar HTTP 500 — para demonstrar retry."""

ERROR_429_RATE = float(os.getenv("FAKE_API_ERROR_429", "0.10"))
"""Probabilidade (0–1) de retornar HTTP 429 — para demonstrar backoff."""

# ── Geração do dataset sintético na inicialização ─────────────────────────
random.seed(42)  # semente fixa → dados reproduzíveis a cada restart

PLANS = ["basic", "standard", "premium"]
REGIONS = ["SP", "RJ", "MG", "RS", "BA", "PR", "SC", "CE"]
GENDERS = ["M", "F", "NB"]

def _generate_customers(n: int) -> list[dict]:
    """
    Gera n clientes sintéticos de streaming com campos realistas para churn.

    Cada cliente tem:
        - customer_id  : identificador único (C0001 … C{n})
        - plan         : plano de assinatura (basic, standard, premium)
        - region       : estado do Brasil
        - age          : idade (18–70)
        - tenure_months: tempo de assinatura (1–120 meses)
        - monthly_spend: gasto mensal em R$ (29.90 – 99.90)
        - churned       : se cancelou (0 ou 1) — label do nosso modelo
        - signup_date   : data de cadastro
    """
    customers = []
    for i in range(1, n + 1):
        plan = random.choice(PLANS)
        tenure = random.randint(1, 120)
        # Clientes de plano basic com baixo tenure têm mais chance de churn
        churn_prob = 0.45 if plan == "basic" and tenure < 6 else 0.15
        customers.append({
            "customer_id":   f"C{i:04d}",
            "plan":          plan,
            "region":        random.choice(REGIONS),
            "age":           random.randint(18, 70),
            "gender":        random.choice(GENDERS),
            "tenure_months": tenure,
            "monthly_spend": round(random.uniform(29.90, 99.90), 2),
            "churned":       int(random.random() < churn_prob),
            "signup_date":   _random_date(),
        })
    logger.info("Dataset gerado: %d clientes sintéticos (seed=42)", n)
    return customers


def _random_date() -> str:
    """Gera uma data aleatória entre 2020-01-01 e 2024-12-31."""
    start = time.mktime(time.strptime("2020-01-01", "%Y-%m-%d"))
    end   = time.mktime(time.strptime("2024-12-31", "%Y-%m-%d"))
    ts    = random.uniform(start, end)
    return time.strftime("%Y-%m-%d", time.localtime(ts))


# Dados gerados uma única vez quando o servidor sobe
ALL_CUSTOMERS: list[dict] = _generate_customers(TOTAL_CUSTOMERS)

# ── Aplicação FastAPI ──────────────────────────────────────────────────────
app = FastAPI(
    title="Fake Streaming API",
    description=(
        "Servidor local de demonstração para o Ep 01 da Trilha MLOps. "
        "Simula uma API de clientes com paginação, autenticação e falhas aleatórias."
    ),
    version="1.0.0",
)


def _check_auth(authorization: Optional[str]) -> None:
    """
    Valida o Bearer Token recebido no header Authorization.

    Lança HTTPException 401 se o token estiver ausente ou incorreto.
    Isso demonstra ao vivo que o collect_api.py envia corretamente o token.
    """
    if not authorization:
        logger.warning("Requisição sem header Authorization")
        raise HTTPException(status_code=401, detail="Authorization header ausente")

    # Formato esperado: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Formato inválido: use 'Bearer <token>'")

    if parts[1] != VALID_TOKEN:
        logger.warning("Token inválido recebido: %s…", parts[1][:8])
        raise HTTPException(status_code=401, detail="Token inválido")


def _maybe_fail() -> None:
    """
    Injeta falhas aleatórias para demonstrar retry e backoff exponencial ao vivo.

    - 30% de chance → HTTP 500 (erro interno do servidor — retryable)
    - 10% de chance → HTTP 429 (rate limit — retryable com backoff)

    Ao gravar, o viewer vê no terminal do servidor qual falha foi injetada,
    e no terminal da pipeline vê o retry do tenacity sendo acionado.
    """
    rng = random.random()

    if rng < ERROR_500_RATE:
        logger.warning(
            "💥 Injetando erro 500 (prob=%.0f%%) — o retry deve ser acionado",
            ERROR_500_RATE * 100,
        )
        raise HTTPException(status_code=500, detail="Erro interno simulado — teste o retry!")

    if rng < ERROR_500_RATE + ERROR_429_RATE:
        logger.warning(
            "⏱  Injetando erro 429 (prob=%.0f%%) — backoff exponencial em ação",
            ERROR_429_RATE * 100,
        )
        raise HTTPException(
            status_code=429,
            detail="Rate limit atingido — aguarde e tente novamente",
            headers={"Retry-After": "2"},
        )


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/v1/customers")
def list_customers(
    page:      int   = Query(default=1,   ge=1,  description="Número da página (começa em 1)"),
    page_size: int   = Query(default=500, ge=1, le=1000, description="Registros por página"),
    authorization: Optional[str] = Header(default=None),
) -> JSONResponse:
    """
    Retorna uma página de clientes de streaming.

    Response body:
        {
            "items":    [...],        # lista de clientes desta página
            "has_next": true/false,   # há mais páginas?
            "page":     1,            # página atual
            "total":    1500          # total de registros
        }

    Possíveis erros (propositais para demonstração):
        401 — Token ausente ou inválido
        429 — Rate limit (aleatório, ~10%)
        500 — Erro interno  (aleatório, ~30%)
    """
    _check_auth(authorization)
    _maybe_fail()  # ← injeta falha aleatória para demonstrar retry

    # Paginação — fatia o dataset sintético
    start = (page - 1) * page_size
    end   = start + page_size
    items = ALL_CUSTOMERS[start:end]

    has_next = end < len(ALL_CUSTOMERS)

    logger.info(
        "GET /v1/customers?page=%d&page_size=%d → %d registros (has_next=%s)",
        page, page_size, len(items), has_next,
    )

    return JSONResponse({
        "items":    items,
        "has_next": has_next,
        "page":     page,
        "total":    len(ALL_CUSTOMERS),
    })


@app.get("/health")
def health_check() -> dict:
    """Endpoint de saúde — útil para confirmar que o servidor subiu."""
    return {
        "status":   "ok",
        "total":    len(ALL_CUSTOMERS),
        "token":    VALID_TOKEN[:4] + "…",  # nunca expõe o token completo
    }


@app.get("/")
def root() -> dict:
    """Endpoint raiz — lista os endpoints disponíveis."""
    return {
        "message": "Fake Streaming API — Ep 01 MLOps",
        "endpoints": {
            "GET /v1/customers": "Lista clientes com paginação",
            "GET /health":       "Status do servidor",
        },
        "config": {
            "total_customers": len(ALL_CUSTOMERS),
            "error_500_rate":  f"{ERROR_500_RATE:.0%}",
            "error_429_rate":  f"{ERROR_429_RATE:.0%}",
        },
    }


# ── Entrada principal ──────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("=" * 55)
    logger.info("  FAKE STREAMING API — Trilha MLOps · Ep 01")
    logger.info("=" * 55)
    logger.info("  URL base  : http://127.0.0.1:8000/v1")
    logger.info("  Token     : %s", VALID_TOKEN)
    logger.info("  Clientes  : %d", len(ALL_CUSTOMERS))
    logger.info("  Erro 500  : %.0f%% das requisições", ERROR_500_RATE * 100)
    logger.info("  Erro 429  : %.0f%% das requisições", ERROR_429_RATE * 100)
    logger.info("-" * 55)
    logger.info("  Configure o .env:")
    logger.info("    API_BASE_URL=http://127.0.0.1:8000/v1")
    logger.info("    API_TOKEN=%s", VALID_TOKEN)
    logger.info("=" * 55)

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
