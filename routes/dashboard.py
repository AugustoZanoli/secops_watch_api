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


# Conta usuários com sub-score alto (>=80) em cada dimensão de risco — proxy de
# "tipo de anomalia" enquanto o banco não tem uma categorização explícita.
@dashboard_bp.get("/anomaly-types")
def get_anomaly_types():
    row = query(
        """
        SELECT COUNT(*) FILTER (WHERE login_score >= 80)    AS login_atipico,
               COUNT(*) FILTER (WHERE computer_score >= 80) AS computadores_atipicos,
               COUNT(*) FILTER (WHERE volume_score >= 80)   AS volume_atipico,
               COUNT(*) FILTER (WHERE redteam_score >= 80)  AS atividade_redteam
        FROM user_risk
        """,
        one=True,
    )
    data = [
        {"type": "Login atípico", "count": row["login_atipico"]},
        {"type": "Computadores atípicos", "count": row["computadores_atipicos"]},
        {"type": "Volume atípico", "count": row["volume_atipico"]},
        {"type": "Atividade Red Team", "count": row["atividade_redteam"]},
    ]
    data.sort(key=lambda item: item["count"], reverse=True)
    return jsonify(data)


# Números gerais de red team (sinais reais de comprometimento no dataset).
@dashboard_bp.get("/redteam-summary")
def get_redteam_summary():
    row = query(
        "SELECT total_redteam_events, affected_users, source_computers, target_computers "
        "FROM redteam_summary LIMIT 1",
        one=True,
    )
    if row is None:
        return jsonify({"error": "no redteam data"}), 404
    return jsonify(row)
