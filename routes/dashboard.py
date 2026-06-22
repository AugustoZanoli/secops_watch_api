from flask import Blueprint, jsonify
from db import get_connection

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/kpis")
def get_kpis():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM dashboard_kpis
        LIMIT 1
    """)

    row = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify({
        "total_logins": row[1],
        "total_users": row[2],
        "total_computers": row[3],
        "period_days": row[4],
        "avg_logins_per_day": row[5]
    })