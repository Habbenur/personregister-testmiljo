---
Projektet är skapat som en del av examinationsuppgift.
---

GDPR – Anonymiserad testdata (Faker-baserad)
Detta projekt använder Faker för att skapa realistisk testdata som därefter automatiskt anonymiseras enligt GDPR-principer.

🔹 Hur fungerar det?
Vid första körning skapas rå testdata (namn, e-post, personnummer, adress) med hjälp av Faker.
All testdata anonymiseras automatiskt:
name → Anonym Användare
email → hashad identifierare (@anon.test)
personnummer → 000000-0000
address → REDACTED
En anonymiserings-guard körs:
vid varje uppstart
samt minst en gång per dag
Om någon testpost inte är anonymiserad korrigeras den automatiskt.

🔹 Automatiska kontroller
Projektet innehåller enhetstester som verifierar att:
rå testdata kan skapas
anonymisering fungerar korrekt
ingen icke-anonym testdata finns kvar
Tester kan köras lokalt eller via Docker:

docker compose run --rm app python app.py --test

🔹 CI/CD
Vid varje push eller pull request körs tester automatiskt via GitHub Actions för att säkerställa att:
beroenden installeras korrekt
applikationen kompilerar
anonymiseringslogiken fungerar som förväntat

Usage

Projektet körs helt via Docker och kräver inga lokala Python-installationer utöver Docker.

🔹 Förutsättningar

Docker

Docker Compose

🔹 Bygg Docker-imagen

I projektets rotkatalog:

    docker compose build --no-cache


--no-cache säkerställer att alla beroenden (t.ex. Faker) installeras korrekt.

🔹 Kör applikationen (engångskörning)

Applikationen körs som engångscontainer enligt CI/CD-principer:

    docker compose run --rm app python app.py


Vid körning:

testdata skapas automatiskt om databasen är tom

anonymisering appliceras

GDPR-kontroll utförs

🔹 Vanliga kommandon
Skapa rå testdata (innan anonymisering)

    docker compose run --rm app python app.py seed -n 10

Anonymisera all testdata

    docker compose run --rm app python app.py anonymize

Kontrollera anonymiseringsstatus

    docker compose run --rm app python app.py check

Lista testdata (endast anonymiserad data)

    docker compose run --rm app python app.py list

Rensa all testdata

    docker compose run --rm app python app.py clear

🔹 Köra tester

Projektet innehåller automatiska enhetstester för anonymisering och dataintegritet.

Kör tester lokalt via Docker:


    docker compose run --rm app python app.py --test

🔹 CI/CD

Alla tester körs automatiskt via GitHub Actions vid varje push eller pull request.
Detta säkerställer att anonymiseringslogiken fortsätter fungera korrekt över tid.

✅ Sammanfattning

Ingen lokal Python-konfiguration krävs

Alla kommandon körs isolerat i Docker

Testdata anonymiseras automatiskt

GDPR-krav verifieras kontinuerligt via tester och CI/CD