from flask import Flask
from flask_cors import CORS

from config import Config

from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

app.register_blueprint(
    dashboard_bp,
    url_prefix="/api/dashboard"
)

if __name__ == "__main__":
    app.run(
        debug=True
    )