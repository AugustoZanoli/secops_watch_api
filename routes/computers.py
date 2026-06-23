from flask import Blueprint, jsonify, request

from db import query, parse_int

computers_bp = Blueprint("computers", __name__)


# Lista as máquinas mais acessadas.
@computers_bp.get("/top")
def top_computers():
    limit = parse_int(request.args.get("limit"), default=10, minimum=1, maximum=100)
    rows = query(
        """
        SELECT computer_id, access_count, unique_users
        FROM top_computers
        ORDER BY access_count DESC
        LIMIT %s
        """,
        (limit,),
    )
    return jsonify(rows)
