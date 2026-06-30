# SecOps Watch — API Reference

## Endpoints

```
GET /api/health
GET /api/dashboard/kpis
GET /api/dashboard/daily-logins
GET /api/dashboard/top-users
GET /api/dashboard/top-computers
GET /api/dashboard/user-risk
GET /api/dashboard/risk-summary
```

---

## Configuração

**Base URL (dev):** `http://localhost:5000`

O Vite já tem proxy em `vite.config.js`:
```js
proxy: { '/api': 'http://localhost:5000' }
```
No front usa só `fetch("/api/...")` sem precisar do host.

**CORS** liberado para `http://localhost:5173`.

---

## Formato padrão de erro

Todo erro vem em JSON, nunca em HTML.

```json
{ "error": "mensagem descritiva" }
```

| Código | Quando |
|--------|--------|
| 404 | Rota ou recurso não existe |
| 500 | Erro interno |
| 503 | Banco indisponível |

---

## Avisos importantes (leia antes de codar)

- **`daily-logins.day` é uma data ISO** (`YYYY-MM-DD`). É **sintética**: o dataset não tem data real, então o índice do dia foi ancorado em **2024-01-01** (dia 0). Use como eixo X de data normal.
- **`user-risk.risk_level` vem em português:** `"Alto"`, `"Médio"`, `"Baixo"`. Só existem **3 níveis** (a tabela do Gold não tem tier "Crítico"). Pra um 4º tier, dá pra derivar do `risk_score` (0–100) no front.

---

## Detalhe dos endpoints

### `GET /api/health`

Checa se a API e o banco estão de pé.

```json
{ "status": "ok", "db": "up" }
```
503 com `"db": "down"` se o banco caiu.

---

### `GET /api/dashboard/kpis`

Números gerais (cards do topo). Objeto único.

```json
{
  "total_logins": 708304516,
  "total_users": 11361,
  "total_computers": 22283,
  "period_days": 274,
  "avg_logins_per_day": 2585052.97
}
```

---

### `GET /api/dashboard/daily-logins`

Logins por dia, ordenado por `day` crescente. Array.

```json
[
  { "day": "2024-01-01", "login_count": 3020038, "is_low_volume_day": false },
  { "day": "2024-01-06", "login_count": 499695,  "is_low_volume_day": true  }
]
```
`is_low_volume_day: true` = dia de volume atipicamente baixo (dá pra destacar no gráfico).

---

### `GET /api/dashboard/top-users`

Usuários que mais logaram, ordenado por `login_count` decrescente. Array (todos; fatie no front).

```json
[
  { "user_id": "U12", "login_count": 29331375, "unique_computers": 254 },
  { "user_id": "U13", "login_count": 21576178, "unique_computers": 26  }
]
```

---

### `GET /api/dashboard/top-computers`

Máquinas mais acessadas, ordenado por `access_count` decrescente. Array.

```json
[
  { "computer_id": "C148", "access_count": 24622287, "unique_users": 887  },
  { "computer_id": "C219", "access_count": 14284645, "unique_users": 1136 }
]
```

---

### `GET /api/dashboard/user-risk`

Todos os usuários com dados de risco, ordenado por `risk_score` decrescente. Array.
Consumido pela tabela de ranking **e** pelo donut de severidade.

```json
[
  {
    "user_id": "U926",
    "login_count": 48642,
    "unique_computers": 191,
    "risk_level": "Alto",
    "risk_score": 100
  }
]
```
`risk_level` ∈ `"Alto" | "Médio" | "Baixo"`.

---

### `GET /api/dashboard/risk-summary`

Contagem de usuários por nível (atalho pré-agregado pro donut, se não quiser contar no front).

```json
{ "Alto": 112, "Médio": 453, "Baixo": 10796, "total": 11361 }
```

---

## Como rodar o backend

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"
cd backend
pip install -r requirements.txt
Copy-Item .env.example .env   # preencher DB_PASSWORD
flask run                     # http://localhost:5000
```

**`.env`:**
```
DB_URL=localhost
DB_PORT=5433
DB_NAME=auth_analytics
DB_USER=postgres
DB_PASSWORD=sua_senha
DEBUG=False
```

> O Postgres roda na porta **5433** (não 5432).
