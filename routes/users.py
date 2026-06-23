from flask import Blueprint, jsonify, request

from db import query, parse_int

users_bp = Blueprint("users", __name__)

RISK_LEVELS = {"HIGH", "MEDIUM", "LOW"}
RISK_ORDER_COLUMNS = {"risk_score", "login_count", "unique_computers"}


# Lista os usuários que mais logaram.
@users_bp.get("/top")
def top_users():
    limit = parse_int(request.args.get("limit"), default=10, minimum=1, maximum=100)
    rows = query(
        """
        SELECT user_id, login_count, unique_computers
        FROM top_users
        ORDER BY login_count DESC
        LIMIT %s
        """,
        (limit,),
    )
    return jsonify(rows)


# Lista os usuários por risco, com filtro de nível e paginação.
@users_bp.get("/risk")
def users_risk():
    limit = parse_int(request.args.get("limit"), default=50, minimum=1, maximum=200)
    offset = parse_int(request.args.get("offset"), default=0, minimum=0)

    order = request.args.get("order", "risk_score")
    if order not in RISK_ORDER_COLUMNS:
        order = "risk_score"

    where = ""
    params = []
    level = request.args.get("level")
    if level:
        level = level.upper()
        if level not in RISK_LEVELS:
            return (
                jsonify({"error": f"invalid level '{level}', use one of {sorted(RISK_LEVELS)}"}),
                400,
            )
        where = "WHERE risk_level = %s"
        params.append(level)

    params.extend([limit, offset])
    rows = query(
        f"""
        SELECT user_id, login_count, unique_computers, risk_level, risk_score
        FROM user_risk
        {where}
        ORDER BY {order} DESC
        LIMIT %s OFFSET %s
        """,
        tuple(params),
    )
    return jsonify(rows)


# Mostra os dados de risco de um usuário específico.
@users_bp.get("/risk/<user_id>")
def user_risk_detail(user_id):
    row = query(
        """
        SELECT user_id, login_count, unique_computers, risk_level, risk_score
        FROM user_risk
        WHERE user_id = %s
        """,
        (user_id,),
        one=True,
    )
    if row is None:
        return jsonify({"error": f"user '{user_id}' not found"}), 404
    return jsonify(row)
