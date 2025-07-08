from flask import Blueprint, request, jsonify
from ..models import db, Topic
from flask import session

topic_bp = Blueprint('topic_bp', __name__)

@topic_bp.route('/topics', methods=['GET'])
def get_topics():
    topics = Topic.query.all()
    return jsonify([
        {'id': t.id, 'name': t.name, 'description': t.description}
        for t in topics
    ])

@topic_bp.route('/topics', methods=['POST'])
def create_topic():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({'error': 'Naziv teme je obavezan'}), 400

    topic = Topic(name=name, description=description)
    db.session.add(topic)
    db.session.commit()

    return jsonify({'message': 'Tema uspešno kreirana'}), 201

@topic_bp.route('/topics/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    data = request.get_json()
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Tema nije pronađena'}), 404

    topic.name = data.get('name', topic.name)
    topic.description = data.get('description', topic.description)

    db.session.commit()
    return jsonify({'message': 'Tema ažurirana'}), 200

@topic_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Tema nije pronađena'}), 404

    db.session.delete(topic)
    db.session.commit()
    return jsonify({'message': 'Tema obrisana'}), 200
