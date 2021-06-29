from flask_login import UserMixin

from app.app import db
from werkzeug.security import generate_password_hash, check_password_hash

presentation_user = db.Table('presentation_user',
                             db.Column('presentations_id', db.Integer, db.ForeignKey('presentations.id')),
                             db.Column('users_id', db.Integer, db.ForeignKey('users.id')))


class Presentation(db.Model):
    __tablename__ = 'presentations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    users = db.relationship('User', secondary='presentation_user',
                            backref=db.backref('presentations', lazy='dynamic'))

    schedule = db.relationship('Schedule', cascade="all,delete", backref='presentation')

    @property
    def serialize(self):
        users = list(map(lambda x: x.serialize, self.users))
        """Возвращает данные в сериализуемом формате."""
        return {
            'id': self.id,
            'name': self.name,
            'text': self.text,
            'users': users
        }

    def __str__(self):
        return self.name


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    schedule = db.relationship('Schedule', cascade="all,delete", backref='room')

    @property
    def serialize(self):
        """Возвращает данные в сериализуемом формате."""
        return {
            'id': self.id,
            'name': self.name
        }

    def __str__(self):
        return self.name


class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    date_start = db.Column(db.Date, nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    @property
    def serialize(self):
        """Возвращает данные в сериализуемом формате."""
        return {
            'id': self.id,
            'date_start': str(self.date_start),
            'presentation_id': self.presentation_id,
            'room_id': self.room_id
        }

    def __str__(self):
        return f'{self.date_start} - {self.room_id}'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def serialize(self):
        name_role = Role.query.filter_by(id=self.role_id).first()
        """Возвращает данные в сериализуемом формате."""
        return {
            'id': self.id,
            'name': self.name,
            'role': name_role.name
        }

    def __str__(self):
        return self.name


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __str__(self):
        return self.name
