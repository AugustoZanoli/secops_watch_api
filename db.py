import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config


# Erro de banco usado pelas rotas.
class DatabaseError(Exception):
    pass


def get_connection():
    return psycopg2.connect(
        host=Config.DB_URL,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
    )


# Roda uma query no banco e devolve as linhas.
def query(sql, params=None, one=False):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        if one:
            return rows[0] if rows else None
        return rows
    except psycopg2.Error as exc:
        raise DatabaseError(str(exc)) from exc
    finally:
        if conn is not None:
            conn.close()


# Testa se o banco está respondendo.
def ping():
    try:
        query("SELECT 1")
        return True
    except DatabaseError:
        return False


# Converte um texto da URL em número e segura dentro de um limite.
def parse_int(value, default, minimum=0, maximum=None):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    if n < minimum:
        return minimum
    if maximum is not None and n > maximum:
        return maximum
    return n
