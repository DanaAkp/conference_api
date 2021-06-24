from flask import jsonify, abort, make_response, request

from app.app import app, db
from app.models import Presentation, Schedule, Room, Role, User
from datetime import datetime


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# region Presentation
@app.route('/conference/api/presentations', methods=['GET'])
def get_presentations():
    return jsonify(json_list=[i.serialize for i in Presentation.query.all()])


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['GET'])
def get_presentation(presentation_id):
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    if presentation is None:
        abort(404)
    return jsonify(presentation.serialize)


@app.route('/conference/api/presentations', methods=['POST'])
def create_presentation():
    if not request.json or 'name' not in request.json or 'text' not in request.json:
        abort(400)
    if Presentation.query.filter_by(name=request.json['name']).first() is not None:
        abort(409, f'Presentation with this name is exist.')
    new_presentation = Presentation(name=request.json['name'], text=request.json['text'])
    db.session.add(new_presentation)
    db.session.commit()
    return jsonify(json_list=[i.serialize for i in Presentation.query.all()]), 201


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['PUT'])
def update_presentation(presentation_id):
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    if presentation is None or not request.json or 'name' not in request.json or 'text' not in request.json:
        abort(400)
    presentation.name = request.json['name']
    presentation.text = request.json['text']
    db.session.commit()
    return jsonify(Presentation.query.filter_by(id=presentation_id).first().serialize)


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['DELETE'])
def delete_presentation(presentation_id):
    presentation = Presentation.query.filter_by(id=presentation_id).first()
    if presentation is None:
        abort(404)
    db.session.delete(presentation)
    db.session.commit()
    return jsonify({'result': True})


# endregion


# region Room
@app.route('/conference/api/rooms', methods=['GET'])
def get_rooms():
    return jsonify(json_list=[i.serialize for i in Room.query.all()])


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['GET'])
def get_room(rooms_id):
    room = Room.query.filter_by(id=rooms_id).first()
    if room is None:
        abort(404)
    return jsonify(room.serialize)


@app.route('/conference/api/rooms', methods=['POST'])
def create_room():
    if not request.json or 'name' not in request.json:
        abort(400)
    if Room.query.filter_by(name=request.json['name']).first() is not None:
        abort(409, f'Room is exist.')
    new_room = Room(name=request.json['name'])
    db.session.add(new_room)
    db.session.commit()
    return jsonify(json_list=[i.serialize for i in Room.query.all()]), 201


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['PUT'])
def update_room(rooms_id):
    room = Room.query.filter_by(id=rooms_id).first()
    if room is None or not request.json or 'name' not in request.json:
        abort(400)
    room.name = request.json['name']
    db.session.commit()
    return jsonify(Room.query.filter_by(id=rooms_id).first().serialize)


@app.route('/conference/api/rooms/<int:rooms_id>', methods=['DELETE'])
def delete_room(rooms_id):
    room = Room.query.filter_by(id=rooms_id).first()
    if room is None:
        abort(404)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'result': True})


# endregion


# region Schedule
@app.route('/conference/api/schedule', methods=['GET'])
def get_schedule():
    return jsonify(json_list=[i.serialize for i in Schedule.query.all()])


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['GET'])
def get_record_in_schedule(schedule_id):
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    if schedule is None:
        abort(404)
    return jsonify(schedule.serialize)


@app.route('/conference/api/schedule', methods=['POST'])
def create_record_in_schedule():
    if not request.json or 'date_start' not in request.json or 'presentation_id' not in request.json or \
            'room_id' not in request.json:
        abort(400)
    if Schedule.query.filter_by(room_id=request.json['room_id'],
                                date_start=request.json['date_start']).first() is not None:
        abort(409, f'Room is busy in this time.')
    new_room = Schedule(room_id=request.json['room_id'], date_start=request.json['date_start'],
                        presentation_id=request.json['presentation_id'])
    db.session.add(new_room)
    db.session.commit()
    return jsonify(json_list=[i.serialize for i in Schedule.query.all()]), 201


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    # TODO правильно ли по id обращаться к расписанию
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    if schedule is None or not request.json or 'room_id' not in request.json or 'presentation_id' not in request.json \
            or 'date_start' not in request.json:
        abort(400)
    schedule.room_id = request.json['room_id']
    schedule.presentation_id = request.json['presentation_id']
    schedule.date_start = request.json['date_start']
    db.session.commit()
    return jsonify(Schedule.query.filter_by(id=schedule_id).first().serialize)


@app.route('/conference/api/schedule/<int:schedule_id>', methods=['DELETE'])
def delete_record_in_schedule(schedule_id):
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    if schedule is None:
        abort(404)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'result': True})
# endregion
