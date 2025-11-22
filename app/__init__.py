from flask import Flask
from flask_cors import CORS

from .config import Config
from .models.db import db
from .services.embedding_service import EmbeddingService
from .services.recommender_service import RecommenderService


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Init DB
    db.init_app(app)

    with app.app_context():
        # Import models so SQLAlchemy knows them
        from .models.internship import Internship  # noqa: F401

        db.create_all()

        # Initialize embedding + recommender services
        embedding_service = EmbeddingService()
        recommender_service = RecommenderService(embedding_service)

        # Build FAISS index from existing internships
        recommender_service.rebuild_index()

        # Store in app.extensions (safe, no circular import)
        app.extensions["embedding_service"] = embedding_service
        app.extensions["recommender_service"] = recommender_service

    # Import and register blueprints AFTER app is ready
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/")

    return app
