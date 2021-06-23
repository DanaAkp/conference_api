from flask import jsonify

from app import app, db
from models import Presentation, Schedule, Room


@app.route('/')
def hello_world():
    return 'Hello World!'


# region Presentation
@app.route('/conference/api/presentations', methods=['GET'])
def get_presentations():
    presentation = Presentation.query.all()
    print(presentation, type(presentation))
    return jsonify(json_list=presentation)
    # return "presentation"  # TODO json


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['GET'])
def get_presentation(presentation_id):
    pass


@app.route('/conference/api/presentations', methods=['POST'])
def create_presentation():
    pass


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['PUT'])
def update_presentation(presentation_id):
    pass


@app.route('/conference/api/presentations/<int:presentation_id>', methods=['DELETE'])
def delete_presentation(presentation_id):
    pass

# endregion



