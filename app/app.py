from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy(app)

from models import Schedule, Room, User, Role, Presentation


def is_room_busy(date_start, id_room) -> bool:
    """Метод, определяющий занята ли аудитория в выбранное время.
    Если занята, то возвращает True, иначе - False."""

    presentation_at_time = Schedule.query.filter_by(id_room=int(id_room), date_start=datetime.
                                                    strptime(date_start, '%Y-%m-%d %H:%M:%S')).first()
    if presentation_at_time is None:
        return False
    return True


from views import *
