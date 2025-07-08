from flask import Blueprint, request, jsonify
from ..models import db, LikeDislike, User, Discussion

vote_bp = Blueprint('votes', __name__)

@vote_bp.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    user_id = data.get('user_id')
    discussion_id = data.get('discussion_id')
    is_like = data.get('is_like')  # true = like, false = dislike

    if not all([user_id, discussion_id, is_like in [True, False]]):
        return jsonify({'error': 'Nedostaju podaci ili su neispravni'}), 400

    # Proveri da li je glas već dat
    existing = LikeDislike.query.filter_by(user_id=user_id, discussion_id=discussion_id).first()
    if existing:
        # Ažuriraj postojeći glas
        existing.is_like = is_like
    else:
        vote = LikeDislike(user_id=user_id, discussion_id=discussion_id, is_like=is_like)
        db.session.add(vote)

    db.session.commit()
    return jsonify({'message': 'Glas uspešno zabeležen'})

@vote_bp.route('/discussions/<int:discussion_id>/votes', methods=['GET'])
def get_vote_counts(discussion_id):
    likes = LikeDislike.query.filter_by(discussion_id=discussion_id, is_like=True).count()
    dislikes = LikeDislike.query.filter_by(discussion_id=discussion_id, is_like=False).count()
    return jsonify({'likes': likes, 'dislikes': dislikes})

