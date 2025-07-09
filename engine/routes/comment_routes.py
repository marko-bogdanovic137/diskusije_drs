from flask import Blueprint, request, jsonify
from ..models import db, Comment, User, Discussion
from ..email_utils import send_email
import re

comment_bp = Blueprint('comments', __name__)

# Kreiranje komentara
@comment_bp.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    content = data.get('content')
    user_id = data.get('user_id')
    discussion_id = data.get('discussion_id')

    # Validacija
    if not all([content, user_id, discussion_id]):
        return jsonify({'error': 'Missing data'}), 400

    # Kreiranje i čuvanje komentara
    comment = Comment(
        content=content,
        user_id=user_id,
        discussion_id=discussion_id
    )
    db.session.add(comment)
    db.session.commit()

    mentions = re.findall(r'@(\w+)', content)
    print("Detektovani mentions:", mentions)

    for username in mentions:
        mentioned_user = User.query.filter_by(username=username).first()
        if mentioned_user:
            subject = "Pomenuti ste u komentaru"
            body = (
                f"Pozdrav {mentioned_user.first_name},\n\n"
                f"Korisnik {comment.user.username} vas je pomenuo u komentaru "
                f"na diskusiji #{discussion_id}.\n\n"
                f"Tekst komentara:\n{content}\n\n"
                f"Pozdrav,\nPlatforma za diskusije"
            )
            print(f"Šaljem email na: {mentioned_user.email}")
            send_email(mentioned_user.email, subject, body)

    return jsonify({'message': 'Komentar dodat', 'id': comment.id}), 201

# Listanje komentara za jednu diskusiju
@comment_bp.route('/comments/<int:discussion_id>', methods=['GET'])
def get_comments(discussion_id):
    comments = Comment.query.filter_by(discussion_id=discussion_id).all()
    result = []
    for c in comments:
        result.append({
            'id': c.id,
            'content': c.content,
            'author': c.user.username,
            'created_at': c.created_at.isoformat()
        })
    return jsonify(result)

# Brisanje komentara
@comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    data = request.get_json()
    user_id = data.get('user_id')

    comment = Comment.query.get_or_404(comment_id)

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Korisnik ne postoji'}), 404

    if comment.user_id != user_id and not user.is_admin and comment.discussion.user_id != user_id:
        return jsonify({'error': 'Nemate dozvolu da obrisete ovaj komentar'}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Komentar obrisan'}), 200
