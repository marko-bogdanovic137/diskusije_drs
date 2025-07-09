# Diskusije – Flask + MySQL aplikacija

Cilj je napraviti platformu za diskusije sa registracijom, administracijom korisnika, objavama i osnovnim društvenim funkcijama.

## ⚙️ Pokretanje API-ja (lokalno)

1. Kloniraj repozitorijum i pozicioniraj se u root folder:
cd diskusije-projekat

2. Pokreni pipenv okruženje i instaliraj biblioteke:
pipenv shell
pipenv install

3. Postavi `.env` fajl u `engine/` folder (primer sadržaja):
DB_USER=root
DB_PASSWORD=1337
DB_HOST=localhost
DB_PORT=3306
DB_NAME=diskusije
SECRET_KEY=supertajna123

4. Pokreni aplikaciju:
cd engine
python app.py


Aplikacija je tada dostupna na: [http://localhost:5000](http://localhost:5000)

## Baza podataka

- Baza: MySQL (lokalni server)
- Šema: `diskusije`
- Alat za migracije: Flask-Migrate

Postojeće tabele:

- `users` – korisnički podaci + status odobrenja
- `discussions` – diskusije objavljene od strane korisnika
- `alembic_version` – interna tabela za praćenje migracija
- `comments` - tabela komentara koji su vezani za roditeljsku diskusiju
-`likes_dislikes` - tabela koja prati statistiku lajkova/dislajkova za roditeljsku diskusiju
-`topics` - tabela tema

## Struktura projekta
diskusije-projekat/
│
├── engine/
│ ├── app.py # Glavna Flask aplikacija (API servis)
│ ├── extensions.py # SQLAlchemy + Migrate ekstenzije
│ ├── models.py # SQLAlchemy modeli (User, Discussion)
│ ├── email_utils # setovan sistem mailovanja
│ ├── 
│ ├── routes/
│ │ ├── auth_routes.py # Rute za registraciju, login, admin potvrdu
│ │ ├── discussion_routes.py # Rute za diskusije (GET, POST)
│ │ ├── comment_routes.py # Komentari
│ │ ├── topic_routes # Teme
│ │ └── vote_routes # lajkovi/dsilajkovi
│ ├── migrations/ # Flask-Migrate fajlovi
│ └── .env # Environment varijable
│ └── templates/ #html stranice
│
├── Pipfile
├── Pipfile.lock
├── README.md
├── dev-log.md
└── .gitignore

## Tehnologije koje se koriste

- Python 3.13
- Flask
- SQLAlchemy
- Flask-Migrate
- Pipenv
- MySQL 
- Postman 
- Git 

