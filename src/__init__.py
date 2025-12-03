from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    from .config import config
    app.config.from_object(config["development"])
    
    db.init_app(app) 
    with app.app_context():
        db.create_all()
        
    return app
