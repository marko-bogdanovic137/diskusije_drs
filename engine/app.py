from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from .extensions import db, migrate
from .models import User, Discussion, Topic, LikeDislike
from .routes.auth_routes import auth_bp
from .routes.comment_routes import comment_bp
from .routes.discussion_routes import discussion_bp
from .routes.vote_routes import vote_bp
from .routes.topic_routes import topic_bp
import requests
import os

# Učitavanje .env fajla
load_dotenv()

app = Flask(__name__)

# Konfiguracija baze

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tajni-kljuc')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(discussion_bp, url_prefix='/api')
app.register_blueprint(comment_bp, url_prefix='/api')
app.register_blueprint(vote_bp, url_prefix='/api')
app.register_blueprint(topic_bp, url_prefix='/api')



# Inicijalizacija ekstenzija
db.init_app(app)
migrate.init_app(app, db)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/', methods=['GET'])
def index():
    title_filter = request.args.get('title', '')
    author_filter = request.args.get('author', '')
    topic_filter = request.args.get('topic', '')

    query = Discussion.query.join(User).join(Topic)

    if title_filter:
        query = query.filter(Discussion.title.ilike(f'%{title_filter}%'))

    if author_filter:
        query = query.filter(User.username.ilike(f'%{author_filter}%'))

    if topic_filter:
        query = query.filter(Topic.name.ilike(f'%{topic_filter}%'))

    discussions = query.order_by(Discussion.created_at.desc()).all()

    # Dodavanje lajkova/dislajkova u rezultat
    result = []
    for d in discussions:
        likes = LikeDislike.query.filter_by(discussion_id=d.id, is_like=True).count()
        dislikes = LikeDislike.query.filter_by(discussion_id=d.id, is_like=False).count()
        result.append({
            'discussion': d,
            'likes': likes,
            'dislikes': dislikes
        })

    return render_template('index.html', discussions=result)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']

        for field in required_fields:
            if not data.get(field):
                flash(f'Nedostaje polje: {field}', 'danger')
                return render_template('register.html')

        # Provera da li već postoji korisnik
        if User.query.filter_by(email=data['email']).first():
            flash('Email već postoji', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=data['username']).first():
            flash('Korisničko ime već postoji', 'danger')
            return render_template('register.html')

        # Kreiranje korisnika
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

        flash('Uspešno ste se registrovali. Sačekajte odobrenje administratora.', 'success')
        return redirect('/')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_ui():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # šaljemo POST ka API-ju
        response = requests.post('http://localhost:5000/api/login', json={
            'email': email,
            'password': password
        })

        if response.status_code == 200:
            data = response.json()
            session['user_id'] = data['user']['id']
            session['username'] = data['user']['username']
            session['is_admin'] = data['user']['is_admin']
            return redirect(url_for('index'))
        else:
            flash(response.json().get('error', 'Greška prilikom prijave'))

    return render_template('login.html')

@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('index'))

    response = requests.get('http://localhost:5000/api/pending-users')
    users = response.json() if response.status_code == 200 else []
    return render_template('admin.html', users=users)

@app.route('/admin/pending-users')
def pending_users_ui():
    if not session.get('is_admin'):
        flash('Nemate pristup ovoj stranici.')
        return redirect(url_for('index'))

    # Pozivamo API da uzmemo listu korisnika
    response = requests.get('http://localhost:5000/api/pending-users')

    if response.status_code == 200:
        users = response.json()
        return render_template('pending_users.html', users=users)
    else:
        flash('Greška prilikom učitavanja korisnika.')
        return redirect(url_for('index'))


@app.route('/admin/approve/<int:user_id>', methods=['POST'])
def approve_user_ui(user_id):
    if not session.get('is_admin'):
        flash('Nemate dozvolu.')
        return redirect(url_for('index'))

    response = requests.post(f'http://localhost:5000/api/approve/{user_id}')
    if response.status_code == 200:
        flash('Korisnik odobren.')
    else:
        flash('Greška pri odobravanju.')
    return redirect(url_for('pending_users_ui'))


@app.route('/admin/reject/<int:user_id>', methods=['POST'])
def reject_user_ui(user_id):
    if not session.get('is_admin'):
        flash('Nemate dozvolu.')
        return redirect(url_for('index'))

    response = requests.post(f'http://localhost:5000/api/reject/{user_id}')
    if response.status_code == 200:
        flash('Korisnik odbijen.')
    else:
        flash('Greška pri odbijanju.')
    return redirect(url_for('pending_users_ui'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/discussions/add', methods=['GET', 'POST'])
def add_discussion_ui():
    if 'user_id' not in session:
        flash("Morate biti prijavljeni da biste kreirali diskusiju.", "warning")
        return redirect(url_for('login'))

    topics = Topic.query.all()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        topic_id = request.form['topic_id']
        user_id = session['user_id']

        if not (title and content and topic_id):
            flash("Sva polja su obavezna.", "danger")
            return redirect(url_for('add_discussion_ui'))

        discussion = Discussion(title=title, content=content, topic_id=topic_id, user_id=user_id)
        db.session.add(discussion)
        db.session.commit()
        flash("Diskusija uspešno kreirana.", "success")
        return redirect(url_for('index'))

    return render_template("add_discussion.html", topics=topics)

@app.route('/delete-discussion/<int:discussion_id>', methods=['POST'])
def delete_discussion_ui(discussion_id):
    if 'user_id' not in session:
        flash('Morate biti prijavljeni da biste obrisali diskusiju.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    is_admin = session.get('is_admin', False)

    # Provera da li korisnik ima pravo da briše
    discussion = Discussion.query.get(discussion_id)
    if not discussion:
        flash('Diskusija nije pronađena.', 'warning')
        return redirect(url_for('index'))

    if discussion.user_id != user_id and not is_admin:
        flash('Nemate dozvolu da obrišete ovu diskusiju.', 'danger')
        return redirect(url_for('index'))

    # Pozivamo backend API koji briše diskusiju
    response = requests.delete(
        f'http://localhost:5000/api/discussions/{discussion_id}',
        json={'user_id': user_id}
    )

    if response.status_code == 200:
        flash('Diskusija je obrisana.', 'success')
    else:
        flash(response.json().get('error', 'Greška prilikom brisanja.'), 'danger')

    return redirect(url_for('index'))


@app.route('/discussions/<int:discussion_id>/edit', methods=['GET', 'POST'])
def edit_discussion_ui(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    topics = Topic.query.all()

    # Dozvoljeno samo autoru diskusije ili adminu
    if session.get('user_id') != discussion.user_id and not session.get('is_admin'):
        flash("Nemate dozvolu da izmenite ovu diskusiju.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        discussion.title = request.form['title']
        discussion.content = request.form['content']
        discussion.topic_id = int(request.form['topic_id'])

        db.session.commit()
        flash("Diskusija uspešno izmenjena.", "success")
        return redirect(url_for('index'))

    return render_template('edit_discussion.html', discussion=discussion, topics=topics)


@app.route('/admin/topics')
def topics_ui():
    if not session.get('is_admin'):
        flash('Nemate pristup ovoj stranici.', 'danger')
        return redirect(url_for('index'))

    topics = Topic.query.all()
    return render_template('topics.html', topics=topics)


@app.route('/admin/topics/delete/<int:topic_id>', methods=['POST'])
def delete_topic_ui(topic_id):
    if not session.get('is_admin'):
        flash('Nemate pristup.', 'danger')
        return redirect(url_for('index'))

    topic = Topic.query.get(topic_id)
    if not topic:
        flash('Tema nije pronađena.', 'warning')
        return redirect(url_for('topics_ui'))

    if topic.discussions:
        flash("Ne možete obrisati temu jer postoje diskusije koje je koriste.", "danger")
        return redirect(url_for('topics_ui'))

    db.session.delete(topic)
    db.session.commit()
    flash('Tema obrisana.', 'success')
    return redirect(url_for('topics_ui'))


@app.route('/admin/topics/add', methods=['GET', 'POST'])
def add_topic_ui():
    if not session.get('is_admin'):
        flash('Nemate pristup.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name:
            flash('Naziv je obavezan.', 'warning')
            return redirect(url_for('add_topic_ui'))

        topic = Topic(name=name, description=description)
        db.session.add(topic)
        db.session.commit()
        flash('Tema uspešno dodata.', 'success')
        return redirect(url_for('topics_ui'))

    return render_template('add_topic.html')

@app.route('/admin/topics/edit/<int:topic_id>', methods=['GET', 'POST'])
def edit_topic_ui(topic_id):
    if not session.get('is_admin'):
        flash('Nemate pristup.', 'danger')
        return redirect(url_for('index'))

    topic = Topic.query.get_or_404(topic_id)

    if request.method == 'POST':
        topic.name = request.form['name']
        topic.description = request.form['description']
        db.session.commit()
        flash('Tema uspešno izmenjena.', 'success')
        return redirect(url_for('topics_ui'))

    return render_template('edit_topic.html', topic=topic)

@app.route('/discussion/<int:discussion_id>', methods=['GET', 'POST'])
def view_discussion(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)

    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Morate biti prijavljeni da biste ostavili komentar.', 'danger')
            return redirect(url_for('login'))

        content = request.form['content']
        if not content.strip():
            flash('Komentar ne može biti prazan.', 'warning')
            return redirect(request.url)

        response = requests.post('http://localhost:5000/api/comments', json={
            'content': content,
            'user_id': session['user_id'],
            'discussion_id': discussion_id
        })

        if response.status_code == 201:
            flash('Komentar dodat.', 'success')
        else:
            flash('Greška pri dodavanju komentara.', 'danger')

        return redirect(request.url)

    response = requests.get(f'http://localhost:5000/api/comments/{discussion_id}')
    comments = response.json() if response.status_code == 200 else []

    return render_template('view_discussion.html', discussion=discussion, comments=comments)

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment_ui(comment_id):
    if 'user_id' not in session:
        flash('Morate biti prijavljeni.', 'danger')
        return redirect(url_for('login'))

    # Radi redirekcije nazad na diskusiju
    discussion_id = request.args.get('discussion_id', type=int)

    response = requests.delete(f'http://localhost:5000/api/comments/{comment_id}', json={
        'user_id': session['user_id']
    })

    if response.status_code == 200:
        flash('Komentar obrisan.', 'success')
    else:
        flash(response.json().get('error', 'Greška prilikom brisanja.'), 'danger')

    return redirect(url_for('view_discussion', discussion_id=discussion_id))

@app.route('/api/vote', methods=['POST'])
def vote_ui():
    data = request.get_json()

    user_id = data.get('user_id')
    discussion_id = data.get('discussion_id')
    is_like = data.get('is_like')

    if not all([user_id, discussion_id]) or is_like not in [True, False]:
        return jsonify({'error': 'Neispravni podaci'}), 400

    existing = LikeDislike.query.filter_by(user_id=user_id, discussion_id=discussion_id).first()
    if existing:
        existing.is_like = is_like
    else:
        new_vote = LikeDislike(user_id=user_id, discussion_id=discussion_id, is_like=is_like)
        db.session.add(new_vote)

    db.session.commit()
    return jsonify({'message': 'Glas zabeležen'}), 200

