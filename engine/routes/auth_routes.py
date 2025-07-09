from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session
from ..models import User
from ..extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validacija ulaza
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Nedostaje polje: {field}'}), 400

    # Provera duplikata
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email već postoji'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Korisničko ime već postoji'}), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        address=data.get('address'),
        city=data.get('city'),
        country=data.get('country'),
        phone=data.get('phone'),
        is_admin=False,
        is_approved=False  
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Uspešno registrovan. Čekajte odobrenje administratora.'}), 201


@auth_bp.route('/pending-users', methods=['GET'])
def get_pending_users():
    pending = User.query.filter_by(is_approved=False).all()

    output = []
    for user in pending:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "address": user.address,
            "city": user.city,
            "country": user.country,
            "phone": user.phone
        }
        output.append(user_data)

    return jsonify(output), 200

@auth_bp.route('/approve/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Korisnik nije pronađen'}), 404

    if user.is_approved:
        return jsonify({'message': 'Korisnik je već odobren'}), 400

    user.is_approved = True
    db.session.commit()
    return jsonify({'message': f'Korisnik {user.username} je odobren'}), 200


@auth_bp.route('/reject/<int:user_id>', methods=['POST'])
def reject_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Korisnik nije pronađen'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'Korisnik {user.username} je odbijen i obrisan'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email i lozinka su obavezni'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'Korisnik ne postoji'}), 404

    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Pogrešna lozinka'}), 401

    if not user.is_approved:
        return jsonify({'error': 'Nalog nije odobren od strane administratora'}), 403

    return jsonify({
        'message': 'Uspešno prijavljen',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Korisnik nije pronađen'}), 404

    requester_id = data.get('requesting_user_id')
    requester = User.query.get(requester_id)
    if not requester:
        return jsonify({'error': 'Nevažeći ID onoga ko šalje zahtev'}), 400

    if requester.id != user.id and not requester.is_admin:
        return jsonify({'error': 'Nemate dozvolu da menjate ovaj nalog'}), 403

    editable_fields = [
        'username', 'email', 'password', 'first_name', 'last_name',
        'address', 'city', 'country', 'phone'
    ]

    for field in editable_fields:
        if field in data:
            if field == 'password':
                setattr(user, field, generate_password_hash(data[field]))
            else:
                setattr(user, field, data[field])

    db.session.commit()

    return jsonify({'message': 'Nalog je uspešno izmenjen'}), 200
