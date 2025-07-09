from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from ..models import db, Discussion, User, Topic, Comment

discussion_bp = Blueprint('discussion_bp', __name__)

@discussion_bp.route('/discussions', methods=['POST'])
def create_discussion():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    topic = data.get('topic_id')
    user_id = data.get('user_id')

    if not all([title, content, topic, user_id]):
        return jsonify({'error': 'Sva polja su obavezna'}), 400
    
    topic = Topic.query.get(topic)
    if not topic:
        return jsonify({'error': 'Tema nije pronadjena'}), 404

    discussion = Discussion(
        title=title,
        content=content,
        topic=topic,
        user_id=user_id
    )
    db.session.add(discussion)
    db.session.commit()

    return jsonify({'message': 'Diskusija uspesno kreirana'}), 201


@discussion_bp.route('/discussions', methods=['GET'])
def get_discussions():
    discussions = Discussion.query.order_by(Discussion.created_at.desc()).all()
    return jsonify([
        {
            'id': d.id,
            'title': d.title,
            'content': d.content,
            'topic': d.topic_id,
            'user_id': d.user_id,
            'created_at': d.created_at.isoformat()
        }
        for d in discussions
    ])


@discussion_bp.route('/discussions/<int:discussion_id>', methods=['DELETE'])
def delete_discussion(discussion_id):
    data = request.get_json()
    user_id = data.get('user_id')

    discussion = Discussion.query.get(discussion_id)
    if not discussion:
        return jsonify({'error': 'Diskusija nije pronadjena'}), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Korisnik ne postoji'}), 404

    # Dozvoljeno je da brise autor ili admin
    if discussion.user_id != user_id and not user.is_admin:
        return jsonify({'error': 'Nemate dozvolu da obrišete ovu diskusiju'}), 403

    Comment.query.filter_by(discussion_id=discussion.id).delete()

    db.session.delete(discussion)
    db.session.commit()
    return jsonify({'message': 'Diskusija i povezani komentari obrisani'}), 200


@discussion_bp.route('/discussions/search', methods=['GET'])
def search_discussions():
    topic = request.args.get('topic')
    creator = request.args.get('creator')
    title = request.args.get('title')

    query = Discussion.query

    if topic:
        query = query.filter(Discussion.topic.ilike(f"%{topic}%"))

    if title:
        query = query.filter(Discussion.title.ilike(f"%{title}%"))

    if creator:
        query = query.join(User).filter(User.username.ilike(f"%{creator}%"))

    results = query.order_by(Discussion.created_at.desc()).all()

    return jsonify([
        {
            'id': d.id,
            'title': d.title,
            'content': d.content,
            'topic': d.topic.name,
            'user_id': d.user_id,
            'created_at': d.created_at.isoformat()
        }
        for d in results
    ])

@discussion_bp.route('/discussions/<int:discussion_id>', methods=['PUT'])
def update_discussion(discussion_id):
    data = request.get_json()
    user_id = data.get('user_id') 

    discussion = Discussion.query.get(discussion_id)
    if not discussion:
        return jsonify({'error': 'Diskusija nije pronađena'}), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Korisnik ne postoji'}), 404

    # Dozvola: vlasnik diskusije ili admin
    if discussion.user_id != user_id and not user.is_admin:
        return jsonify({'error': 'Nemate dozvolu da izmenite ovu diskusiju'}), 403

    title = data.get('title')
    content = data.get('content')
    topic = data.get('topic')

    if title:
        discussion.title = title
    if content:
        discussion.content = content
    if topic:
        discussion.topic = topic

    db.session.commit()
    return jsonify({'message': 'Diskusija izmenjena'}), 200


