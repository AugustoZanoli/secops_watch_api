from flask import Blueprint, jsonify

from db import query

computers_bp = Blueprint("computers", __name__)


# Lista as máquinas mais acessadas (top 100 pré-calculado no banco).
@computers_bp.get("/top-computers")
def get_top_computers():
    rows = query(
        """
        SELECT computer AS computer_id,
               total_authentications,
               success_logins,
               failed_logins,
               active_days,
               avg_daily_authentications,
               max_daily_authentications,
               redteam_source_events,
               redteam_target_events,
               unique_users
        FROM top_computers
        ORDER BY total_authentications DESC
        """
    )
    return jsonify(rows)
