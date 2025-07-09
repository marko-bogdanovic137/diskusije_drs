
# Dev Log – Platforma za diskusije

## Dan 1

- Instalirao Python i pipenv
- Instalirao MySQL i napravio novu semu `diskusije`
- Napravio osnovni Flask API (folder `engine`)
- Napravio `User` model
- Podesio konekciju na bazu pomocu `.env`
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
- Updateovao `README.md`

## Dan 4

- Omogućena izmena korisnickog profila (PUT /update-profile/<user_id>)
- Dodata validacija inputa i zastita korisničkih podataka
- Dodate preostale tabele, resen problem sa constraintovima
- Implementirana vecina backend funkcija u frontend


## Dan 5
- Dodata opcija za izmenu korisnickog profila
- Ispravljeni razni bugovi
- Zavrsene preostale implementacije koje su nedostajale



