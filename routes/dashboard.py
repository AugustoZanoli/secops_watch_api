from datetime import date, timedelta

from flask import Blueprint, jsonify

from db import query

dashboard_bp = Blueprint("dashboard", __name__)

# 01/01/2024 usado como referência de início (dia 0) -> derivado do índice do dia.
# 2024-01-01 cai numa segunda-feira, então day % 7 == 0 também representa segunda.
DAY_ZERO = date(2024, 1, 1)


# Pega os números gerais do dashboard.
@dashboard_bp.get("/kpis")
def get_kpis():
    row = query(
        """
        SELECT total_users,
               suspicious_users,
               average_risk,
               authentication_failure_rate,
               critical_users,
               high_users,
               medium_users,
               low_users,
               after_hours_logins
        FROM dashboard_kpis
        LIMIT 1
        """,
        one=True,
    )
    if row is None:
        return jsonify({"error": "no kpi data"}), 404
    return jsonify(row)


# Devolve a série diária de autenticações (day vira data a partir de DAY_ZERO).
@dashboard_bp.get("/login-timeline")
def get_login_timeline():
    rows = query(
        """
        SELECT day, authentications, success_logins, failed_logins, after_hours_logins
        FROM login_timeline
        ORDER BY day ASC
        """
    )
    for r in rows:
        r["day"] = (DAY_ZERO + timedelta(days=r["day"])).isoformat()
    return jsonify(rows)


# Agrega hourly_activity num padrão semanal (dia da semana x hora) pro heatmap 7x24.
@dashboard_bp.get("/activity-heatmap")
def get_activity_heatmap():
    rows = query(
        """
        SELECT day % 7 AS dow,
               hour,
               SUM(authentications)::bigint AS authentications,
               SUM(success_logins)::bigint AS success_logins,
               SUM(failed_logins)::bigint AS failed_logins
        FROM hourly_activity
        GROUP BY dow, hour
        ORDER BY dow, hour
        """
    )
    return jsonify(rows)
