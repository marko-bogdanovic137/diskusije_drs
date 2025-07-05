
# Dev Log – Platforma za diskusije

> Pratim sve što radim na projektu, dan po dan. Ideja je da mogu na kraju da objasnim šta sam sve radio i da ne zaboravim nijedan detalj. Nisam ranije radio full stack projekat ovako, pa idem korak po korak uz pomoć asistenta.

---

## Dan 1

- Instalirao Python i pipenv
- Instalirao MySQL i napravio novu šemu `diskusije`
- Napravio osnovni Flask API (folder `engine`)
- Napravio `User` model
- Podesio konekciju na bazu pomoću `.env`
- Pokrenuo migracije, povezalo se s bazom

## Dan 2

- Dodao rute za registraciju korisnika
- Administrator vidi pending korisnike
- Može da ih odobri/odbije (API testiran preko Postman-a)
- Napravljen `auth_routes.py` i sve testirano ručno
- Postavio git, commitovao osnovne stvari

## Dan 3

- Napravio `Discussion` model i migrirao u bazu
- Napisao rute: `POST` i `GET` diskusije
- Dodao `discussion_routes.py` i povezao u `app.py`
- Testirao u Postman-u sa pravim podacima (user_id, topic, itd.)
- Updateovao `README.md` i nastavio da pišem ovaj log

---

## Plan za dalje

- Komentari
- Like/dislike
- Mention sistem i email obaveštenja
- WebSocket za automatsko osvežavanje zahteva (ako stignem)

---

## Tehnologije

- Python + Flask
- SQLAlchemy + Flask-Migrate
- MySQL lokalni server
- Pipenv
- Postman (testiranje API-ja)
- Git + GitHub

---

