# SecOps Watch — API Reference

## Endpoints disponíveis

```
GET /api/health
GET /api/dashboard/kpis
GET /api/dashboard/login-trend
GET /api/dashboard/risk-summary
GET /api/users/top?limit=N
GET /api/users/risk?level=&order=&limit=&offset=
GET /api/users/risk/<user_id>
GET /api/computers/top?limit=N
```

---

## Configuração

**Base URL (dev):** `http://localhost:5000`

O Vite já tem proxy configurado em `vite.config.js`:
```js
proxy: { '/api': 'http://localhost:5000' }
```
Ou seja, no front usa só `fetch("/api/...")` sem precisar colocar o host.

**CORS** liberado para `http://localhost:5173`.

---

## Formato padrão de erro

Todo erro vem em JSON, nunca em HTML.

```json
{ "error": "mensagem descritiva" }
```

| Código | Quando acontece |
|--------|----------------|
| 400 | Parâmetro inválido (ex: `level=BANANA`) |
| 404 | Rota ou recurso não existe |
| 500 | Erro interno do servidor |
| 503 | Banco de dados indisponível |

---

## Endpoints

### `GET /api/health`

Checa se a API e o banco estão de pé. Bom pra usar antes de renderizar a tela.

**Resposta 200 (banco ok):**
```json
{ "status": "ok", "db": "up" }
```

**Resposta 503 (banco caiu):**
```json
{ "status": "ok", "db": "down" }
```

---

### `GET /api/dashboard/kpis`

Números gerais do dashboard. Usa nos cards do topo.

**Resposta:**
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

### `GET /api/dashboard/login-trend`

Volume de logins por dia. Usa no gráfico de linha temporal.

> `day` é o **número do dia** (0, 1, 2...), não uma data.
> `is_low_volume_day: true` marca dias com volume atipicamente baixo — destaque no gráfico.

**Resposta:**
```json
[
  { "day": 0, "login_count": 3020038, "is_low_volume_day": false },
  { "day": 1, "login_count": 3181039, "is_low_volume_day": false },
  { "day": 5, "login_count": 499695,  "is_low_volume_day": true  }
]
```

---

### `GET /api/dashboard/risk-summary`

Contagem de usuários por nível de risco. Usa no card ou gráfico de pizza de risco.

**Resposta:**
```json
{ "HIGH": 112, "MEDIUM": 453, "LOW": 10796, "total": 11361 }
```

---

### `GET /api/users/top`

Usuários que mais logaram, ordenados por volume.

**Query params:**

| Param | Tipo | Default | Limite |
|-------|------|---------|--------|
| `limit` | inteiro | 10 | 1–100 |

**Exemplo:** `/api/users/top?limit=5`

**Resposta:**
```json
[
  { "user_id": "U12",   "login_count": 29331375, "unique_computers": 254 },
  { "user_id": "U13",   "login_count": 21576178, "unique_computers": 26  },
  { "user_id": "U4148", "login_count": 11933146, "unique_computers": 7   }
]
```

---

### `GET /api/users/risk`

Lista de usuários com score de risco. A tabela tem ~11k linhas — use paginação.

**Query params:**

| Param | Tipo | Default | Valores aceitos |
|-------|------|---------|----------------|
| `level` | string | (todos) | `HIGH`, `MEDIUM`, `LOW` (case-insensitive) |
| `order` | string | `risk_score` | `risk_score`, `login_count`, `unique_computers` |
| `limit` | inteiro | 50 | 1–200 |
| `offset` | inteiro | 0 | ≥ 0 |

A ordenação é sempre **decrescente**.

**Exemplos:**
```
/api/users/risk
/api/users/risk?level=HIGH
/api/users/risk?level=HIGH&order=login_count&limit=20&offset=0
/api/users/risk?limit=50&offset=50   ← página 2
```

**Resposta:**
```json
[
  {
    "user_id": "U926",
    "login_count": 48642,
    "unique_computers": 191,
    "risk_level": "HIGH",
    "risk_score": 100
  }
]
```

**Erro 400** (level inválido):
```json
{ "error": "invalid level 'BANANA', use one of ['HIGH', 'LOW', 'MEDIUM']" }
```

---

### `GET /api/users/risk/<user_id>`

Detalhe de um usuário específico.

**Exemplo:** `/api/users/risk/U926`

**Resposta 200:**
```json
{
  "user_id": "U926",
  "login_count": 48642,
  "unique_computers": 191,
  "risk_level": "HIGH",
  "risk_score": 100
}
```

**Resposta 404** (usuário não existe):
```json
{ "error": "user 'U999' not found" }
```

---

### `GET /api/computers/top`

Máquinas mais acessadas, ordenadas por volume.

**Query params:**

| Param | Tipo | Default | Limite |
|-------|------|---------|--------|
| `limit` | inteiro | 10 | 1–100 |

**Exemplo:** `/api/computers/top?limit=10`

**Resposta:**
```json
[
  { "computer_id": "C148", "access_count": 24622287, "unique_users": 887  },
  { "computer_id": "C219", "access_count": 14284645, "unique_users": 1136 }
]
```

---

## Como rodar o backend

```powershell
# Adicionar Postgres ao PATH (necessário a cada sessão nova)
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"

cd caminho/para/backend

pip install -r requirements.txt

# Copiar e preencher o .env
Copy-Item .env.example .env
notepad .env

flask run
# API disponível em http://localhost:5000
```

**Conteúdo do `.env`:**
```
DB_URL=localhost
DB_PORT=5433
DB_NAME=auth_analytics
DB_USER=postgres
DB_PASSWORD=sua_senha
DEBUG=False
```

> O Postgres roda na porta **5433** (não 5432). Não esquecer isso no `.env`.
