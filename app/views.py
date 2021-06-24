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

# endregion



