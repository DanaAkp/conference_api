import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']
db = SQLAlchemy(app)
login_manager = LoginManager(app)
admin = Admin(app)

from app.models import Schedule, Room, User, Role, Presentation, generate_password_hash

db.create_all()

admin.add_view(ModelView(Presentation, db.session))
admin.add_view(ModelView(Schedule, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(User, db.session))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def insert_test_data():
    db.drop_all()
    db.create_all()
    roles = [Role(name='admin'), Role(name='presenter'), Role(name='listener')]

    users = [User(name='admin', role_id=1, password_hash=generate_password_hash('password')),
             User(name='presenter', role_id=2, password_hash=generate_password_hash('password')),
             User(name='listener', role_id=3, password_hash=generate_password_hash('password'))]

    presentations = [Presentation(name='presentation 1', text='presentation text'),
                     Presentation(name='presentation 2', text='presentation text'),
                     Presentation(name='presentation 3', text='presentation text')]
    presentations[0].users.append(users[1])
    rooms = [Room(name='20-505'), Room(name='20-511'), Room(name='20-506')]

    schedule = [Schedule(date_start=datetime(2021, 5, 3), presentation_id=1, room_id=1),
                Schedule(date_start=datetime(2021, 6, 3), presentation_id=2, room_id=2)]

    for i in roles + users + presentations + rooms + schedule:
        db.session.add(i)
        db.session.commit()


from app.views import *
