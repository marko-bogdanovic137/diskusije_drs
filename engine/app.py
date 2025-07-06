from flask import Flask
from dotenv import load_dotenv
from .extensions import db, migrate
from .models import User, Discussion
from .routes.auth_routes import auth_bp
from .routes.comment_routes import comment_bp
from .routes.discussion_routes import discussion_bp
from .routes.vote_routes import vote_bp
import os

# Učitavanje .env fajla
load_dotenv()

app = Flask(__name__)

# Konfiguracija baze

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(discussion_bp, url_prefix='/api')
app.register_blueprint(comment_bp, url_prefix='/api')
app.register_blueprint(vote_bp, url_prefix='/api')


# Inicijalizacija ekstenzija
db.init_app(app)
migrate.init_app(app, db)

@app.route('/')
def hello():
    return "API povezan sa bazom!"

if __name__ == '__main__':
    app.run(debug=True)
