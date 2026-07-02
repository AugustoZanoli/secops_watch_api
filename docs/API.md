# SecOps Watch — API Reference

## Endpoints

```
GET /api/health

GET /api/dashboard/kpis
GET /api/dashboard/login-timeline
GET /api/dashboard/activity-heatmap

GET /api/dashboard/risk-distribution
GET /api/dashboard/user-risk
GET /api/dashboard/top-users

GET /api/dashboard/top-computers
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

- **`login-timeline.day` é uma data ISO** (`YYYY-MM-DD`). É **sintética**: o dataset não tem data real, o índice do dia foi ancorado em **2024-01-01** (dia 0, que é uma segunda-feira).
- **`failed_logins` e `authentication_failure_rate` estão zerados.** As colunas existem no banco (`dashboard_kpis`, `login-timeline`, `activity-heatmap`) mas o pipeline que popula os dados ainda não calcula falhas de autenticação de verdade — hoje toda linha vem com `0`. Isso é um problema de dado upstream, não da API; os campos serão preenchidos quando o pipeline for corrigido.
- **`risk_level` vem em inglês:** `"Critical"`, `"High"`, `"Medium"`, `"Low"` — 4 níveis (diferente da versão anterior da API, que tinha só 3 e traduzia pro português).
- **`activity-heatmap` é um agregado semanal**, não os 58 dias brutos do dataset. `dow` é dia da semana (`0` = segunda, ..., `6` = domingo), calculado como `day % 7` e somado entre todas as semanas do período. Pensado pro heatmap 7×24.
- **`top-users` tem só 100 linhas** (os usuários de maior risco, pré-calculados no banco). Para o dataset completo de risco (12k+ usuários, sem contagem de login) use `user-risk`.
- **Ainda não implementado** (pendente de dado novo do pipeline):
  - KPI de "acessos fora do padrão" — nenhuma coluna do banco corresponde a essa métrica hoje.
  - Breakdown de "tipos de anomalia" — o banco só tem totais agregados de redteam (`redteam_summary`), sem quebra por tipo.

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
  "total_users": 12414,
  "suspicious_users": 3285,
  "average_risk": 50.0,
  "authentication_failure_rate": 0.0,
  "critical_users": 531,
  "high_users": 2754,
  "medium_users": 5306,
  "low_users": 3823,
  "after_hours_logins": 156600476
}
```

---

### `GET /api/dashboard/login-timeline`

Autenticações por dia, ordenado por `day` crescente. Array.

```json
[
  { "day": "2024-01-01", "authentications": 5118366, "success_logins": 5062449, "failed_logins": 0, "after_hours_logins": 1879135 },
  { "day": "2024-01-02", "authentications": 5812321, "success_logins": 5754246, "failed_logins": 0, "after_hours_logins": 2414306 }
]
```

---

### `GET /api/dashboard/activity-heatmap`

Autenticações por dia da semana × hora, somadas entre todas as semanas do período. Array de até 168 linhas (7 × 24).

```json
[
  { "dow": 0, "hour": 0, "authentications": 83931, "success_logins": 82641, "failed_logins": 0 },
  { "dow": 0, "hour": 1, "authentications": 85036, "success_logins": 83722, "failed_logins": 0 }
]
```
`dow`: `0` = segunda-feira ... `6` = domingo.

---

### `GET /api/dashboard/risk-distribution`

Contagem de usuários por nível de risco (atalho pré-agregado pro donut de severidade).

```json
{ "Critical": 531, "High": 2754, "Medium": 5306, "Low": 3823, "total": 12414 }
```

---

### `GET /api/dashboard/user-risk`

Todos os usuários (12k+) com seus scores de risco, ordenado por `risk_score` decrescente. Array.
Não tem contagem de login/acessos — só os sub-scores normalizados (0–100) que compõem o `risk_score`.

```json
[
  {
    "user_id": "U66",
    "risk_score": 99.98,
    "risk_level": "Critical",
    "login_score": 99.99,
    "computer_score": 99.96,
    "volume_score": 99.98,
    "redteam_score": 100.0
  }
]
```

---

### `GET /api/dashboard/top-users`

Os 100 usuários de maior risco, ordenado por `risk_score` decrescente. Array.
Consumido pela tabela de ranking **e** pelo scatter de acessos × score (limitado a esses 100).

```json
[
  {
    "user_id": "U66",
    "risk_score": 99.98,
    "risk_level": "Critical",
    "redteam_events": 118,
    "total_logins": 11182208,
    "unique_computers": 253,
    "active_days": 58,
    "max_daily_authentications": 242890
  }
]
```

---

### `GET /api/dashboard/top-computers`

As 100 máquinas mais acessadas, ordenado por `total_authentications` decrescente. Array.

```json
[
  {
    "computer_id": "C2388",
    "total_authentications": 14256,
    "success_logins": 14250,
    "failed_logins": 0,
    "active_days": 58,
    "avg_daily_authentications": 245.79,
    "max_daily_authentications": 782,
    "redteam_source_events": 0,
    "redteam_target_events": 27,
    "unique_users": 34
  }
]
```

---

## Como rodar o backend

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"
pip install -r requirements.txt
Copy-Item .env.example .env   # preencher DB_PASSWORD
flask run                     # http://localhost:5000
```

**`.env`:**
```
DB_URL=localhost
DB_PORT=5432
DB_NAME=security_watch
DB_USER=postgres
DB_PASSWORD=sua_senha
DEBUG=False
```
