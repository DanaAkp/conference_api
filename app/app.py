import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_wtf import CSRFProtect
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']
db = SQLAlchemy(app)
login_manager = LoginManager(app)
admin = Admin(app)
CSRFProtect(app)

from app.models import Schedule, Room, User, Role, Presentation

db.create_all()

admin.add_view(ModelView(Presentation, db.session))
admin.add_view(ModelView(Schedule, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(User, db.session))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


from app.views import *
