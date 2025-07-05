# Platforma za diskusije

## Arhitektura

Projekat se sastoji iz tri komponente:
- UI: Flask frontend aplikacija (dolazi kasnije)
- Engine: Flask API aplikacija (trenutno implementirana)
- DB: MySQL baza podataka (localhost, šema `diskusije`)

## Tehnologije

- Python 3.13 (pipenv za dependency management)
- Flask, Flask-SQLAlchemy, Flask-Migrate
- MySQL
- Docker (planirano za distribuciju)
- Git + GitHub (za verzionisanje i dokumentaciju)
- WebSocket (planiran za admin panel)

## Pokretanje API-ja

1. Postavi `.env` fajl (primer se nalazi u `engine/.env`)
2. Pokreni virtualno okruženje:
pipenv shell
pipenv install
3. Pokreni aplikaciju:
cd engine
python app.py

## Baza

Kreirana je šema `diskusije` u MySQL.
Trenutno postoji model `User` sa sledećim poljima:
- username, email, password, ime, prezime, adresa, grad, država, telefon
- is_admin (bool), is_approved (bool)

Migracije su omogućene uz Flask-Migrate.

## Uradjeno do sada

- Kreirana struktura projekta
- Povezan API sa MySQL bazom
- Migracije omogućene
- Model korisnika kreiran
- Git repozitorijum postavljen

