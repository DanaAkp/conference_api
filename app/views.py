from flask import jsonify, abort, make_response, request, url_for, redirect, flash, render_template
from flask_login import logout_user, current_user, login_user, login_required

from app.app import app, db
from app.models import Presentation, Schedule, Room, Role, User
from datetime import datetime
from app.forms import RegistrationForm, LoginForm


@app.route('/')
def home():
    return 'Hello, world!'


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# region User authorize
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('get_presentations'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(csrf_enabled=False)
    if request.method == "POST":
        if User.query.filter_by(name=form.username.data).first() is None:
            new_user = User(name=form.username.data, email=form.email.data, role_id=3)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
        else:
            flash('Username is exist')
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)


# endregion


# region Presentation
@app.route('/conference/api/presentations', methods=['GET'])
@login_required
def get_presentations():
    return jsonify(json_list=[i.serialize for i in Presentation.query.all()])


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['GET'])
@login_required
def get_presentation(presentation_id):
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    if presentation is None:
        abort(404)
    return jsonify(presentation.serialize)


@app.route('/conference/api/presentations', methods=['POST'])
@login_required
def create_presentation():
    if current_user.role_id != 2:
        abort(403, f'User cannot create a presentation.')
    if not request.json or 'name' not in request.json or 'text' not in request.json:
        abort(400)
    if Presentation.query.filter_by(name=request.json['name']).first() is not None:
        abort(409, f'Presentation with this name is exist.')
    new_presentation = Presentation(name=request.json['name'], text=request.json['text'])
    db.session.add(new_presentation)
    db.session.commit()
    return jsonify(json_list=[i.serialize for i in Presentation.query.all()]), 201


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['PUT'])
@login_required
def update_presentation(presentation_id):
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    if not len(list(filter(lambda x: x.id == current_user.id, presentation.users))):
        abort(403)
    if presentation is None or not request.json or 'name' not in request.json or 'text' not in request.json:
        abort(400)
    presentation.name = request.json['name']
    presentation.text = request.json['text']
    db.session.commit()
    return jsonify(Presentation.query.filter_by(id=presentation_id).first().serialize)


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['DELETE'])
@login_required
def delete_presentation(presentation_id):
    if current_user.role_id != 1:
        abort(403)
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    if presentation is None:
        abort(404)
    db.session.delete(presentation)
    db.session.commit()
    return jsonify({'result': True})


# endregion


# region Room
@app.route('/conference/api/rooms', methods=['GET'])
@login_required
def get_rooms():
    if current_user.role_id != 1:
        abort(403)
    return jsonify(json_list=[i.serialize for i in Room.query.all()])


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['GET'])
@login_required
def get_room(rooms_id):
    if current_user.role_id != 1:
        abort(403)
    room = Room.query.filter_by(id=rooms_id).first()
    if room is None:
        abort(404)
    return jsonify(room.serialize)


@app.route('/conference/api/rooms', methods=['POST'])
@login_required
def create_room():
    if current_user.role_id != 1:
        abort(403)
    if not request.json or 'name' not in request.json:
        abort(400)
    if Room.query.filter_by(name=request.json['name']).first() is not None:
        abort(409, f'Room is exist.')
    new_room = Room(name=request.json['name'])
    db.session.add(new_room)
    db.session.commit()
    return jsonify(json_list=[i.serialize for i in Room.query.all()]), 201


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['PUT'])
@login_required
def update_room(rooms_id):
    if current_user.role_id != 1:
        abort(403)
    room = Room.query.filter_by(id=rooms_id).first()
    if room is None or not request.json or 'name' not in request.json:
        abort(400)
    room.name = request.json['name']
    db.session.commit()
    return jsonify(Room.query.filter_by(id=rooms_id).first().serialize)


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['DELETE'])
@login_required
def delete_room(rooms_id):
    if current_user.role_id != 1:
        abort(403)
    room = Room.query.filter_by(id=rooms_id).first()
    if room is None:
        abort(404)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'result': True})


# endregion


# region Schedule
@app.route('/conference/api/schedule', methods=['GET'])
@login_required
def get_schedule():
    return jsonify(json_list=[i.serialize for i in Schedule.query.all()])


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['GET'])
@login_required
def get_record_in_schedule(schedule_id):
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    if schedule is None:
        abort(404)
    return jsonify(schedule.serialize)


@app.route('/conference/api/schedule', methods=['POST'])
@login_required
def create_record_in_schedule():
    if current_user.role_id != 1 and current_user.role_id != 2:
        abort(403)
    if not request.json or 'date_start' not in request.json or 'presentation_id' not in request.json or \
            'room_id' not in request.json:
        abort(400)
    if Schedule.query.filter_by(room_id=request.json['room_id'],
                                date_start=request.json['date_start']).first() is not None:
        abort(409, f'Room is busy in this time.')
    date = request.json['date_start'].split('-')
    new_record_in_schedule = Schedule(room_id=request.json['room_id'],
                                      date_start=datetime(int(date[0]), int(date[1]), int(date[2])),
                                      presentation_id=request.json['presentation_id'])
    db.session.add(new_record_in_schedule)
    db.session.commit()
    return jsonify(json_list=[i.serialize for i in Schedule.query.all()]), 201


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    if current_user.role_id != 1 and current_user.role_id != 2:
        abort(403)
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    if schedule is None or not request.json or 'room_id' not in request.json or 'presentation_id' not in request.json \
            or 'date_start' not in request.json:
        abort(400)
    schedule.room_id = request.json['room_id']
    schedule.presentation_id = request.json['presentation_id']
    date = request.json['date_start'].split('-')
    schedule.date_start = datetime(int(date[0]), int(date[1]), int(date[2]))
    db.session.commit()
    return jsonify(Schedule.query.filter_by(id=schedule_id).first().serialize)


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_record_in_schedule(schedule_id):
    if current_user.role_id != 1:
        abort(403)
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    if schedule is None:
        abort(404)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'result': True})
# endregion
