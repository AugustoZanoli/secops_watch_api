# SecOps Watch — Backend

## Pré-requisitos

- Python 3.14
- PostgreSQL rodando localmente

---

## Configuração

**1. Clone o repositório e entre na pasta**
```bash
git clone https://github.com/AugustoZanoli/secops_watch_api.git
cd secops_watch
```

**2. Crie e ative um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure o `.env`**

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:
```bash
cp .env.example .env
```

Preencha com suas credenciais:
```env
DB_URL=localhost
DB_NAME=secops_watch
DB_USER=postgres
DB_PASSWORD=sua_senha
```

**5. Rode o servidor**
```bash
flask run
```

A API estará disponível em `http://localhost:5000`.
