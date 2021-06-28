import requests
from flask import jsonify, abort, make_response, request, url_for, redirect, flash, render_template
from flask_login import logout_user, current_user, login_user, login_required

from app.app import app, db
from app.models import Presentation, Schedule, Room, Role, User
from datetime import datetime


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': error.description}), 404)


@app.errorhandler(403)
def not_found(error):
    return make_response(jsonify({'message': error.description}), 403)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'message': error.description}), 400)


@app.errorhandler(409)
def not_found(error):
    return make_response(jsonify({'message': error.description}), 409)


def check_access_user(role_id: int, error_message):
    """Проверка доступа пользователя по его роли."""
    if current_user.role_id != role_id:
        abort(403, error_message)


def check_for_availability(object_for_check, error_message):
    """Проверка на существование некоторого объекта."""
    if object_for_check is None:
        abort(404, error_message)


# region Presentation
@app.route('/conference/api/presentations', methods=['GET'])
@login_required
def get_presentations():
    return jsonify(json_list=[i.serialize for i in Presentation.query.all()])


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['GET'])
@login_required
def get_presentation(presentation_id):
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    check_for_availability(presentation, 'Presentation with this id was not found.')
    return jsonify(presentation.serialize)


def check_bad_request_for_actions_on_presentation():
    """Проверка неверного запроса для создания или обновления презентации."""
    if not request.json:
        abort(400, 'Request body is required.')
    if 'name' not in request.json:
        abort(400, 'Field name is required.')
    if 'text' not in request.json:
        abort(400, 'Field text is required.')


@app.route('/conference/api/presentations', methods=['POST'])
@login_required
def create_presentation():
    check_access_user(2, 'Only presenter can create a presentation.')
    check_bad_request_for_actions_on_presentation()
    if Presentation.query.filter_by(name=request.json['name']).first() is not None:
        abort(409, 'Presentation with this name already exist.')
    new_presentation = Presentation(name=request.json['name'], text=request.json['text'], users=[current_user])
    db.session.add(new_presentation)
    db.session.commit()
    return jsonify(new_presentation.serialize), 201


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['PUT'])
@login_required
def update_presentation(presentation_id):
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    if not len(list(filter(lambda x: x.id == current_user.id, presentation.users))):
        abort(403, 'Only presentation creator can update a presentation.')
    check_bad_request_for_actions_on_presentation()
    presentation.name = request.json['name']
    presentation.text = request.json['text']
    db.session.commit()
    return jsonify(Presentation.query.filter_by(id=presentation_id).first().serialize)


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['DELETE'])
@login_required
def delete_presentation(presentation_id):
    check_access_user(1, 'Only admin can delete a presentation.')
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    check_for_availability(presentation, 'Presentation with this id was not found.')
    db.session.delete(presentation)
    db.session.commit()
    return jsonify({'result': True})


# endregion


# region Room
@app.route('/conference/api/rooms', methods=['GET'])
@login_required
def get_rooms():
    return jsonify(json_list=[i.serialize for i in Room.query.all()])


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['GET'])
@login_required
def get_room(rooms_id):
    check_access_user(1, 'Only admin can view a room.')
    room = Room.query.filter_by(id=rooms_id).first()
    check_for_availability(room, 'Room with this id was not found.')
    return jsonify(room.serialize)


def check_bad_request_for_actions_on_room():
    """Проверка неверного запроса для создания или обновления аудитории."""
    if not request.json:
        abort(400, 'Request body is required.')
    if 'name' not in request.json:
        abort(400, 'Field name is required.')


@app.route('/conference/api/rooms', methods=['POST'])
@login_required
def create_room():
    check_access_user(1, 'Only admin can create a room.')
    check_bad_request_for_actions_on_room()
    if Room.query.filter_by(name=request.json['name']).first() is not None:
        abort(409, f'Room already exist.')
    new_room = Room(name=request.json['name'])
    db.session.add(new_room)
    db.session.commit()
    return jsonify(new_room.serialize), 201


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['PUT'])
@login_required
def update_room(rooms_id):
    check_access_user(1, 'Only admin can update a room.')
    room = Room.query.filter_by(id=rooms_id).first()
    check_for_availability(room, 'Room with this id was not found.')
    check_bad_request_for_actions_on_room()
    room.name = request.json['name']
    db.session.commit()
    return jsonify(Room.query.filter_by(id=rooms_id).first().serialize)


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['DELETE'])
@login_required
def delete_room(rooms_id):
    check_access_user(1, 'Only admin can delete a room.')
    room = Room.query.filter_by(id=rooms_id).first()
    check_for_availability(room, 'Room with this id was not found.')
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
    check_for_availability(schedule, 'Record with this id was not found in schedule.')
    return jsonify(schedule.serialize)


def check_bad_request_for_actions_on_schedule():
    """Проверка неверного запроса для обновления расписания или создания записи в нем."""
    if not request.json:
        abort(400, 'Request body is required.')
    if 'date_start' not in request.json:
        abort(400, 'Field date start is required.')
    if 'presentation_id' not in request.json:
        abort(400, 'Field presentation is required.')
    if 'room_id' not in request.json:
        abort(400, 'Field room is required.')


@app.route('/conference/api/schedule/check_room_busy', methods=['POST'])
@login_required
def check_busy_room_at_the_time():
    if not request.json:
        abort(400, 'Request body is required.')
    if 'date_start' not in request.json:
        abort(400, 'Field date start is required.')
    if 'room_id' not in request.json:
        abort(400, 'Field room is required.')

    if Schedule.query.filter_by(room_id=request.json['room_id'],
                                date_start=request.json['date_start']).first() is not None:
        return jsonify({'result': False})
    return jsonify({'result': True})


@app.route('/conference/api/schedule', methods=['POST'])
@login_required
def create_record_in_schedule():
    if current_user.role_id != 1 and current_user.role_id != 2:
        abort(403, 'Only admin or presenter can create an entry in the schedule.')
    check_bad_request_for_actions_on_schedule()
    if Schedule.query.filter_by(room_id=request.json['room_id'],
                                date_start=request.json['date_start']).first() is not None:
        abort(409, f'Room is busy in this time.')
    date = request.json['date_start'].split('-')
    new_record_in_schedule = Schedule(room_id=request.json['room_id'],
                                      date_start=datetime(int(date[0]), int(date[1]), int(date[2])),
                                      presentation_id=request.json['presentation_id'])
    db.session.add(new_record_in_schedule)
    db.session.commit()
    return jsonify(new_record_in_schedule.serialize), 201


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    if current_user.role_id != 1 and current_user.role_id != 2:
        abort(403, 'Only admin or presenter can update an entry in the schedule.')
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    check_for_availability(schedule, 'Record with this id was not found in schedule.')
    check_bad_request_for_actions_on_schedule()
    schedule.room_id = request.json['room_id']
    schedule.presentation_id = request.json['presentation_id']
    date = request.json['date_start'].split('-')
    schedule.date_start = datetime(int(date[0]), int(date[1]), int(date[2]))
    db.session.commit()
    return jsonify(Schedule.query.filter_by(id=schedule_id).first().serialize)


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_record_in_schedule(schedule_id):
    check_access_user(1, 'Only admin can delete an entry in the schedule.')
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    check_for_availability(schedule, 'Record with this id was not found in schedule.')
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'result': True})
# endregion
