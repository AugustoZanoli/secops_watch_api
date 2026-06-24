from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from db import DatabaseError, ping

from routes.dashboard import dashboard_bp
from routes.users import users_bp
from routes.computers import computers_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, origins=["http://localhost:5173"])

app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(users_bp, url_prefix="/api/users")
app.register_blueprint(computers_bp, url_prefix="/api/computers")


# Diz se a API e o banco estão de pé.
@app.get("/api/health")
def health():
    db_up = ping()
    return (
        jsonify({"status": "ok", "db": "up" if db_up else "down"}),
        200 if db_up else 503,
    )


@app.errorhandler(DatabaseError)
def handle_db_error(exc):
    return jsonify({"error": "database unavailable", "detail": str(exc)}), 503


@app.errorhandler(404)
def handle_404(_exc):
    return jsonify({"error": "not found"}), 404


@app.errorhandler(500)
def handle_500(_exc):
    return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=Config.DEBUG)
