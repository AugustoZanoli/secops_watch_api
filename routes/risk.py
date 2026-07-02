from flask import Blueprint, jsonify

from db import query

risk_bp = Blueprint("risk", __name__)


# Conta quantos usuários tem em cada nível de risco.
@risk_bp.get("/risk-distribution")
def get_risk_distribution():
    rows = query("SELECT risk_level, users FROM risk_distribution")
    summary = {r["risk_level"]: r["users"] for r in rows}
    summary["total"] = sum(r["users"] for r in rows)
    return jsonify(summary)


# Lista todos os usuários com seus dados de risco, do maior pro menor.
@risk_bp.get("/user-risk")
def get_user_risk():
    rows = query(
        """
        SELECT "user" AS user_id,
               risk_score,
               risk_level,
               login_score,
               computer_score,
               volume_score,
               redteam_score
        FROM user_risk
        ORDER BY risk_score DESC
        """
    )
    return jsonify(rows)


# Lista os usuários com maior risco (top 100 pré-calculado no banco).
@risk_bp.get("/top-users")
def get_top_users():
    rows = query(
        """
        SELECT "user" AS user_id,
               risk_score,
               risk_level,
               redteam_events,
               total_logins,
               unique_computers,
               active_days,
               max_daily_authentications
        FROM top_users
        ORDER BY risk_score DESC
        """
    )
    return jsonify(rows)
