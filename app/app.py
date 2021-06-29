import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap

app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']
db = SQLAlchemy(app)
login_manager = LoginManager(app)
admin = Admin(app)
bootstrap = Bootstrap(app)

from app.models import Schedule, Room, User, Role, Presentation, generate_password_hash

db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.role_id == 1


admin.add_view(MyModelView(Presentation, db.session))
admin.add_view(MyModelView(Schedule, db.session))
admin.add_view(MyModelView(Room, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(User, db.session))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_first_request
def insert_test_data():
    db.drop_all()
    db.create_all()
    roles = [Role(name='admin'), Role(name='presenter'), Role(name='listener')]

    users = [User(name='administrator', role_id=1, password_hash=generate_password_hash('password')),
             User(name='user presenter', role_id=2, password_hash=generate_password_hash('password')),
             User(name='user listener', role_id=3, password_hash=generate_password_hash('password'))]

    for i in roles + users:
        db.session.add(i)
        db.session.commit()


from app.views import *
