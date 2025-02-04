from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.ma import ma
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os
from flask_marshmallow import Marshmallow

from dotenv import load_dotenv

load_dotenv()

# db = SQLAlchemy()
# migrate = Migrate()
# bcrypt = Bcrypt()
# jwt = JWTManager()

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")


    # Print the environment variables to verify
    print(f"SECRET_KEY: {app.config['SECRET_KEY']}")
    print(f"JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")
    

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register blueprints, configure extensions, etc.
    from app import routes
    routes.init_app(app)  # Call init_app to register the root route

    # Import models here to avoid circular imports
    from app.models import Role

    return app