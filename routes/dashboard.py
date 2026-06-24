from flask import Blueprint, jsonify

from db import query

dashboard_bp = Blueprint("dashboard", __name__)


# Pega os números gerais do dashboard.
@dashboard_bp.get("/kpis")
def get_kpis():
    row = query(
        """
        SELECT total_logins,
               total_users,
               total_computers,
               period_days,
               avg_logins_per_day
        FROM dashboard_kpis
        ORDER BY id
        LIMIT 1
        """,
        one=True,
    )
    if row is None:
        return jsonify({"error": "no kpi data"}), 404
    return jsonify(row)


# Devolve quantos logins teve em cada dia.
@dashboard_bp.get("/login-trend")
def get_login_trend():
    rows = query(
        """
        SELECT day, login_count, is_low_volume_day
        FROM daily_login_trend
        ORDER BY day
        """
    )
    return jsonify(rows)


# Conta quantos usuários tem em cada nível de risco.
@dashboard_bp.get("/risk-summary")
def get_risk_summary():
    rows = query(
        """
        SELECT risk_level, COUNT(*) AS count
        FROM user_risk
        GROUP BY risk_level
        """
    )
    summary = {r["risk_level"]: r["count"] for r in rows}
    summary["total"] = sum(r["count"] for r in rows)
    return jsonify(summary)
