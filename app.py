import os

IS_PRODUCTION = os.getenv("RAILWAY_ENVIRONMENT") is not None

if not IS_PRODUCTION:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, render_template  # noqa: E402
from werkzeug.middleware.proxy_fix import ProxyFix  # noqa: E402
from routes.auth import auth_bp  # noqa: E402
from routes.captation import captation_bp  # noqa: E402
from routes.dashboard import dashboard_bp  # noqa: E402

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a_remplacer")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.register_blueprint(auth_bp)
app.register_blueprint(captation_bp)
app.register_blueprint(dashboard_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=not IS_PRODUCTION, port=int(os.getenv("PORT", 5001)), use_reloader=False)
