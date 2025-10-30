from flask import Flask, jsonify
from flask_cors import CORS
import os
from extensions import db, ma  # ✅ use external extension definitions

def create_app():
    app = Flask(__name__, static_folder=None)

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/tracker'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import blueprints AFTER db and ma are initialized
    from src.user_management_module.controllers.user_controller import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')

    # Health check route
    @app.route('/api/ping')
    def ping():
        return jsonify({"status": "ok"})

    return app

# ✅ Create app globally so imports from models work fine
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
