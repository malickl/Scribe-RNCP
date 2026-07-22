from flask import Flask
# from routes.auth import auth_bp
# from routes.captation import captation_bp
# from routes.pipeline import pipeline_bp
# from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = "a_remplacer"

# app.register_blueprint(auth_bp)
# app.register_blueprint(captation_bp)
# app.register_blueprint(pipeline_bp)
# app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
