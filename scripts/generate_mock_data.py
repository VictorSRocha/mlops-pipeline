"""
generate_mock_data.py — Gerador do banco SQLite para desenvolvimento (Parte 2)
==============================================================================
Este script cria o banco SQLite local com tabelas customers e transactions,
usado na demonstração da Parte 2 do Ep 01 (coleta de banco de dados).

Execute:
    python scripts/generate_mock_data.py

O que será criado:
    data/raw/local.db        → banco SQLite com tabelas customers e transactions
    data/raw/watermark.json  → controle de extração incremental

Separação de responsabilidades:
    Parte 2 (banco):  este script ou notebook Parte 2
    Parte 3 (CSVs):   as funções generate_demographics() e generate_support_tickets()
                      abaixo são usadas na demonstração do notebook Parte 3.
                      Os arquivos CSV resultantes são commitados no git diretamente.

Por que dados sintéticos?
- Permite desenvolver e testar a pipeline sem acesso a sistemas reais
- Garante que qualquer um que clonar o repositório possa rodar tudo
- Dados reais geralmente têm restrições de privacidade (LGPD/GDPR)
"""

import json
import random
import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np

# Semente aleatória: garante que os dados gerados sejam SEMPRE os mesmos.
# Sem seed, cada execução geraria dados diferentes — não reproduzível.
# random.seed() afeta o módulo random do Python.
# np.random.seed() afeta o NumPy (usado pelo pandas internamente).
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Diretórios de saída
DATA_DIR = Path("data")
RAW_DIR  = DATA_DIR / "raw"
MOCK_DIR = DATA_DIR / "mock"

RAW_DIR.mkdir(parents=True, exist_ok=True)
MOCK_DIR.mkdir(parents=True, exist_ok=True)

# Configurações do dataset
N_CUSTOMERS    = 1_000   # número de clientes
N_TRANSACTIONS = 5_000   # número de transações (média de 5 por cliente)


def generate_customers(n: int) -> pd.DataFrame:
    """Gera um DataFrame de clientes fictícios.

    Campos gerados:
        customer_id: identificador único (C0001, C0002, ...)
        name:        nome fictício
        email:       email derivado do nome
        plan:        plano de assinatura (basic, standard, premium)
        signup_date: data de cadastro nos últimos 3 anos
        churned:     se o cliente cancelou (0 = ativo, 1 = cancelou)
                     → este é o TARGET que nosso modelo vai prever
    """
    first_names = [
        "Ana", "Bruno", "Carlos", "Diana", "Eduardo", "Fernanda",
        "Gabriel", "Helena", "Igor", "Juliana", "Kevin", "Laura",
        "Marcos", "Natalia", "Otavio", "Patricia", "Rafael", "Sofia"
    ]
    last_names = [
        "Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa",
        "Ferreira", "Rodrigues", "Alves", "Nascimento", "Cardoso"
    ]
    plans = ["basic", "standard", "premium"]
    plan_weights = [0.4, 0.4, 0.2]  # 40% basic, 40% standard, 20% premium

    rows = []
    for i in range(1, n + 1):
        first = random.choice(first_names)
        last  = random.choice(last_names)
        plan  = random.choices(plans, weights=plan_weights)[0]

        # Clientes premium têm menos chance de cancelar (5%),
        # basic têm mais (30%). Simula comportamento realista de churn.
        churn_prob = {"basic": 0.30, "standard": 0.15, "premium": 0.05}[plan]
        churned = 1 if random.random() < churn_prob else 0

        rows.append({
            "customer_id": f"C{i:04d}",
            "name": f"{first} {last}",
            "email": f"{first.lower()}.{last.lower()}{i}@email.com",
            "plan": plan,
            "signup_date": (
                pd.Timestamp("2022-01-01") +
                pd.Timedelta(days=random.randint(0, 3 * 365))
            ).strftime("%Y-%m-%d"),
            "churned": churned,
        })

    df = pd.DataFrame(rows)
    print(f"  Clientes gerados: {len(df)} | Churn rate: {df['churned'].mean():.1%}")
    return df


def generate_transactions(customers_df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Gera transações fictícias vinculadas aos clientes.

    Campos gerados:
        transaction_id: identificador único
        customer_id:    referência ao cliente (foreign key)
        amount:         valor da transação em R$
        event_type:     tipo de evento (login, play, pause, etc.)
        created_at:     timestamp da transação (usado como watermark)
    """
    event_types = ["login", "play", "pause", "search", "add_to_list", "share"]
    customer_ids = customers_df["customer_id"].tolist()

    rows = []
    for i in range(1, n + 1):
        customer_id = random.choice(customer_ids)

        rows.append({
            "transaction_id": f"T{i:06d}",
            "customer_id": customer_id,
            "amount": round(random.uniform(0, 50), 2),
            "event_type": random.choice(event_types),
            # created_at: timestamp nos últimos 6 meses
            # pd.Timestamp.now() - pd.Timedelta(days=...): subtrai dias do timestamp atual
            "created_at": (
                pd.Timestamp.now() -
                pd.Timedelta(days=random.randint(0, 180),
                             hours=random.randint(0, 23),
                             minutes=random.randint(0, 59))
            ).strftime("%Y-%m-%d %H:%M:%S"),
        })

    df = pd.DataFrame(rows)
    # Ordena por created_at para simular dados reais
    df = df.sort_values("created_at").reset_index(drop=True)
    print(f"  Transações geradas: {len(df)}")
    return df


def generate_demographics(customer_ids: list) -> pd.DataFrame:
    """Gera dados demográficos fictícios (arquivo CSV externo).

    Simula uma fonte de dados separada, como um arquivo exportado do CRM.
    """
    estados = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "GO", "PE", "CE"]
    faixas_etarias = ["18-25", "26-35", "36-45", "46-55", "56+"]

    rows = []
    for cid in customer_ids:
        rows.append({
            "customer_id": cid,
            "age_group": random.choice(faixas_etarias),
            "state": random.choice(estados),
            "has_children": random.choice([0, 1]),
            "income_bracket": random.choice(["A", "B", "C", "D"]),
        })

    df = pd.DataFrame(rows)
    print(f"  Demographics gerados: {len(df)}")
    return df


def generate_support_tickets(customer_ids: list) -> pd.DataFrame:
    """Gera tickets de suporte fictícios (arquivo CSV externo).

    Simula um export do sistema de atendimento com histórico de chamados
    por cliente. Vinculado ao customer_id para permitir merge com demographics.
    """
    categories = ["billing", "technical", "cancellation", "upgrade", "general"]
    statuses = ["resolved", "open", "closed"]

    rows = []
    for cid in customer_ids:
        n_tickets = random.randint(0, 5)
        for _ in range(n_tickets):
            rows.append({
                "customer_id": cid,
                "ticket_category": random.choice(categories),
                "ticket_status": random.choice(statuses),
                "response_hours": round(random.uniform(0.5, 72), 1),
            })

    df = pd.DataFrame(rows)
    print(f"  Support tickets gerados: {len(df)}")
    return df


def create_sqlite_database(customers_df: pd.DataFrame, transactions_df: pd.DataFrame) -> None:
    """Cria o banco SQLite com as tabelas customers e transactions.

    SQLite é um banco de dados embutido no Python — não precisa instalar
    nada separado. Perfeito para desenvolvimento local.
    O arquivo .db criado é um banco completo que roda em qualquer lugar.
    """
    db_path = RAW_DIR / "local.db"

    # sqlite3.connect() cria o arquivo .db se não existir.
    # "with conn:" garante que as transações sejam confirmadas (commit)
    # ao sair do bloco, ou revertidas (rollback) em caso de erro.
    with sqlite3.connect(db_path) as conn:

        # to_sql() escreve um DataFrame diretamente em uma tabela SQL.
        # if_exists="replace": recria a tabela se já existir (útil para resetar).
        # index=False: não escreve o índice do DataFrame como coluna.
        customers_df.to_sql("customers", conn, if_exists="replace", index=False)
        transactions_df.to_sql("transactions", conn, if_exists="replace", index=False)

        # Cria índice na coluna created_at para que a query de watermark
        # (WHERE created_at > ?) seja muito mais rápida.
        # Sem índice: o banco lê TODAS as linhas para filtrar (table scan).
        # Com índice: o banco pula direto para as linhas certas (index seek).
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_created_at "
            "ON transactions(created_at)"
        )

    print(f"  Banco SQLite criado: {db_path}")


def create_watermark_initial() -> None:
    """Cria o arquivo de watermark inicial para a primeira execução.

    Define o watermark 7 dias atrás para que a extração incremental
    busque apenas transações recentes (não todas de uma vez).
    Útil para simular uma pipeline que já estava rodando.
    """
    watermark_path = RAW_DIR / "watermark.json"

    # Só cria se não existir — não sobrescreve um watermark real.
    if not watermark_path.exists():
        watermark = {
            "last_value": (
                pd.Timestamp.now() - pd.Timedelta(days=7)
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": pd.Timestamp.now().isoformat(),
        }
        watermark_path.write_text(
            json.dumps(watermark, indent=2),
            encoding="utf-8",
        )
        print(f"  Watermark inicial criado: {watermark_path}")
    else:
        print(f"  Watermark já existe, mantendo: {watermark_path}")


def main() -> None:
    """Cria o banco SQLite com dados sintéticos (Parte 2 do Ep 01).

    As funções generate_demographics() e generate_support_tickets()
    existem neste módulo para referência e são demonstradas inline no
    notebook da Parte 3. Os CSVs resultantes são commitados no git.
    """
    print("=" * 55)
    print("GERANDO BANCO SQLITE DE DESENVOLVIMENTO")
    print("=" * 55)

    print("\n[1/3] Gerando clientes...")
    customers_df = generate_customers(N_CUSTOMERS)

    print("\n[2/3] Gerando transações...")
    transactions_df = generate_transactions(customers_df, N_TRANSACTIONS)

    print("\n[3/3] Criando banco SQLite e watermark...")
    create_sqlite_database(customers_df, transactions_df)
    create_watermark_initial()

    print("\n" + "=" * 55)
    print("BANCO CRIADO COM SUCESSO!")
    print("=" * 55)
    print(f"\nArquivos criados:")
    print(f"  {RAW_DIR}/local.db        → banco SQLite (customers + transactions)")
    print(f"  {RAW_DIR}/watermark.json  → controle de extração incremental")
    print(f"\nCSVs externos (Parte 3):")
    print(f"  Rode o notebook Parte 3 para gerar demographics.csv e support_tickets.csv")
    print(f"\nPróximo passo:")
    print(f"  cp .env.example .env")
    print(f"  python -m src.data.pipeline")


if __name__ == "__main__":
    main()
