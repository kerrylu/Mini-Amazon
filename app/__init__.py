from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB
import os

login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .review import bp as review_bp
    app.register_blueprint(review_bp)

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .products import bp as products_bp
    app.register_blueprint(products_bp)

    path = os.getcwd()
    app.config['IMAGE_UPLOADS'] = path + "/app/static/img/uploads"
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['PNG', 'JPG', 'JPEG', 'GIF']


    return app
