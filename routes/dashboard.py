from flask import Blueprint, jsonify

from db import query

dashboard_bp = Blueprint("dashboard", __name__)

RISK_LABELS = {"HIGH": "Alto", "MEDIUM": "Médio", "LOW": "Baixo"}


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
@dashboard_bp.get("/daily-logins")
def get_daily_logins():
    rows = query(
        """
        SELECT day, login_count, is_low_volume_day
        FROM daily_login_trend
        ORDER BY day ASC
        """
    )
    return jsonify(rows)


# Lista os usuários que mais logaram.
@dashboard_bp.get("/top-users")
def get_top_users():
    rows = query(
        """
        SELECT user_id, login_count, unique_computers
        FROM top_users
        ORDER BY login_count DESC
        """
    )
    return jsonify(rows)


# Lista as máquinas mais acessadas.
@dashboard_bp.get("/top-computers")
def get_top_computers():
    rows = query(
        """
        SELECT computer_id, access_count, unique_users
        FROM top_computers
        ORDER BY access_count DESC
        """
    )
    return jsonify(rows)


# Lista os usuários com seus dados de risco, do maior pro menor.
@dashboard_bp.get("/user-risk")
def get_user_risk():
    rows = query(
        """
        SELECT user_id, login_count, unique_computers, risk_level, risk_score
        FROM user_risk
        ORDER BY risk_score DESC
        """
    )
    for r in rows:
        r["risk_level"] = RISK_LABELS.get(r["risk_level"], r["risk_level"])
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
    summary = {RISK_LABELS.get(r["risk_level"], r["risk_level"]): r["count"] for r in rows}
    summary["total"] = sum(r["count"] for r in rows)
    return jsonify(summary)
