from flask import Blueprint, request, jsonify
from ..models import db, Discussion

discussion_bp = Blueprint('discussion_bp', __name__)

@discussion_bp.route('/discussions', methods=['POST'])
def create_discussion():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    topic = data.get('topic')
    user_id = data.get('user_id')

    if not all([title, content, topic, user_id]):
        return jsonify({'error': 'Sva polja su obavezna'}), 400

    discussion = Discussion(
        title=title,
        content=content,
        topic=topic,
        user_id=user_id
    )
    db.session.add(discussion)
    db.session.commit()

    return jsonify({'message': 'Diskusija uspešno kreirana'}), 201


@discussion_bp.route('/discussions', methods=['GET'])
def get_discussions():
    discussions = Discussion.query.order_by(Discussion.created_at.desc()).all()
    return jsonify([
        {
            'id': d.id,
            'title': d.title,
            'content': d.content,
            'topic': d.topic,
            'user_id': d.user_id,
            'created_at': d.created_at.isoformat()
        }
        for d in discussions
    ])

@discussion_bp.route('/discussions/<int:discussion_id>', methods=['DELETE'])
def delete_discussion(discussion_id):
    data = request.get_json()
    user_id = data.get('user_id')  # Privremeno dok nemamo autentifikaciju

    discussion = Discussion.query.get(discussion_id)
    if not discussion:
        return jsonify({'error': 'Diskusija nije pronađena'}), 404

    if discussion.user_id != user_id:
        return jsonify({'error': 'Nemate dozvolu da obrišete ovu diskusiju'}), 403

    db.session.delete(discussion)
    db.session.commit()
    return jsonify({'message': 'Diskusija obrisana'}), 200

@discussion_bp.route('/discussions/search', methods=['GET'])
def search_discussions():
    title = request.args.get('title')
    topic = request.args.get('topic')
    user_id = request.args.get('user_id')

    query = Discussion.query

    if title:
        query = query.filter(Discussion.title.ilike(f"%{title}%"))
    if topic:
        query = query.filter(Discussion.topic.ilike(f"%{topic}%"))
    if user_id:
        query = query.filter(Discussion.user_id == user_id)

    results = query.order_by(Discussion.created_at.desc()).all()

    return jsonify([
        {
            'id': d.id,
            'title': d.title,
            'content': d.content,
            'topic': d.topic,
            'user_id': d.user_id,
            'created_at': d.created_at.isoformat()
        }
        for d in results
    ])
