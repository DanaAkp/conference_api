import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_wtf import CSRFProtect
from flask_login import LoginManager, current_user

app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']
db = SQLAlchemy(app)
login_manager = LoginManager(app)

CSRFProtect(app)

from app.models import Schedule, Room, User, Role, Presentation


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


from app.views import *
