---
Projektet är skapat som en del av examinationsuppgift.
---

# Personregister – GDPR-anpassad testmiljö

Detta projekt demonstrerar hur personuppgifter kan hanteras säkert och kontrollerat i en testmiljö med hjälp av Docker, automatiserad anonymisering, enhetstester och CI/CD.

Fokus ligger på GDPR-anpassad hantering av testdata, inte på produktionssystem.

# Projektmål

Skapa realistisk testdata med Faker

Säkerställa att inga personuppgifter lämnas oavsiktligt oskyddade

Tydligt separera:

rå data

anonymisering

verifiering

radering

Erbjuda ett reproducerbart arbetsflöde via Docker

Validera funktionalitet automatiskt med tester och GitHub Actions

# Arkitekturöversikt

Språk: Python 3.11

Databas: SQLite

Testdatagenerering: Faker

Containerisering: Docker & Docker Compose

CI/CD: GitHub Actions

Applikationen är medvetet enkel för att tydligt visa GDPR-relaterade designbeslut.

# GDPR – Anonymiserad testdata
Hur fungerar det?

Rå testdata skapas med Faker
(namn, e-post, adress, personnummer-liknande värde)

Data anonymiseras explicit via ett separat kommando

En anonymiserings-guard säkerställer att ingen icke-anonym testdata lämnas kvar av misstag

Alla steg är spårbara, testbara och reproducerbara

# Anonymiseringsregler
Fält	Anonymiserat värde
Namn	Anonym Användare
E-post	Hashat värde som slutar med @anon.test
Personnummer	000000-0000
Adress	REDACTED

# Användning (Usage)

Applikationen körs helt via Docker.
Ingen lokal Python-installation krävs.

# Förutsättningar

    Docker

    Docker Compose

# Bygg applikationen

bash
docker compose build --no-cache

# Skapa rå testdata (Faker)
Rå (icke-anonymiserad) testdata skapas endast explicit med:

bash
docker compose run --rm app python app.py seed -n 5
Detta steg finns för att tydligt kunna demonstrera skillnaden mellan rå och anonymiserad data.

# Lista lagrad data
bash
docker compose run --rm app python app.py list


Före anonymisering → realistisk testdata
Efter anonymisering → endast skyddade värden

# Kontrollera anonymiseringsstatus (read-only)

bash
docker compose run --rm app python app.py check


Exempel på utdata:
total_test_rows=5 non_anonymized=5
Detta kommando ändrar aldrig data och fungerar som en revisions-/kontrollfunktion.

# Anonymisera testdata

bash
docker compose run --rm app python app.py anonymize


All testdata anonymiseras i ett kontrollerat och explicit steg.

# Radera all testdata (Right to Erasure – GDPR)

bash
docker compose run --rm app python app.py clear


Detta tar permanent bort all testdata från databasen.

# Köra automatiska tester

bash
docker compose run --rm app python app.py --test


# Tester verifierar:

skapande av testdata

anonymiseringslogik

guard-beteende

dataintegritet

# CI/CD

GitHub Actions kör automatiskt tester vid:

varje push

varje pull request

Detta säkerställer att anonymiseringslogiken fortsätter fungera korrekt över tid.

# Demo-steg (för användare)

Följande steg demonstrerar hela GDPR-livscykeln:

# Ren start
docker compose down -v
docker compose build --no-cache

# Skapa rå testdata
docker compose run --rm app python app.py seed -n 5

# Visa rå data
docker compose run --rm app python app.py list

# Kontrollera status (icke-anonymiserad)
docker compose run --rm app python app.py check

# Anonymisera data
docker compose run --rm app python app.py anonymize

# Verifiera anonymisering
docker compose run --rm app python app.py check

# Radera all testdata
docker compose run --rm app python app.py clear
docker compose run --rm app python app.py check

# Demonstrerade GDPR-principer

Dataminimering

Explicit anonymisering

Spårbarhet och kontroll (read-only checks)

Rätten att bli raderad (Right to Erasure)

Automatisering och reproducerbarhet

# Designbeslut

Anonymisering är explicit, inte implicit

Kontrollkommandon ändrar aldrig data

Radering är oåterkallelig

Testdata hålls strikt åtskild från produktionslogik

Docker används för att skapa en kontrollerad och inspekterbar miljö

# Tester och CI/CD

Projektet använder GitHub Actions för kontinuerlig integration (CI).

Automatiska tester

Alla enhetstester körs automatiskt vid:

    --> varje push till GitHub

    --> varje pull request

Detta säkerställs via följande trigger i workflow-konfigurationen:
    yaml
    on: [push, pull_request]

Vad testas?

De automatiska testerna verifierar att:

    -- testdata kan skapas korrekt

    -- anonymisering fungerar som förväntat

    -- ingen icke-anonymiserad testdata lämnas kvar

    -- applikationen kan köras utan fel

Om något test misslyckas markeras bygget som misslyckat, vilket förhindrar att felaktig kod går vidare.

# Lokala tester

Tester kan även köras manuellt i Docker-miljö:

docker compose run --rm app python app.py --test

# Sammanfattning

Tester körs automatiskt vid varje kodändring i GitHub

Samma testsvit används lokalt och i CI

Detta säkerställer långsiktig kvalitet och GDPR-efterlevnad


Projektet visar ett rent, testbart och GDPR-medvetet arbetssätt för hantering av personuppgifter i utvecklings- och testmiljöer med moderna verktyg och bästa praxis.


# Docker Desktop – Användning (visuellt demonstrationsläge)

Projektet stöder även ett Docker Desktop-läge för visuell demonstration och manuell hantering av containerns livscykel.

Detta läge är avsett för demonstration och examination.

# Starta Docker Desktop-läge

Från projektets rotkatalog:

docker compose --profile desktop up -d


Resultat:

En långlivad container med namnet personregister-desktop startas

Containern visas i Docker Desktop

Containern kan manuellt startas och stoppas via Docker Desktop-gränssnittet

# Verifiera att containern körs
docker ps


Förväntat resultat:

personregister-desktop   Up ...

# Kör kommandon inuti containern

Alla applikationskommandon kan köras inuti den aktiva containern med docker exec.

# Full demonstrationssekvens för Docker Desktop:
- Starta Docker Desktop-läge
docker compose --profile desktop up -d

- Skapa rå testdata
docker exec personregister-desktop python app.py seed -n 5

- Visa rå data
docker exec personregister-desktop python app.py list

- Kontrollera (icke-anonymiserad data)
docker exec personregister-desktop python app.py check

- Anonymisera data
docker exec personregister-desktop python app.py anonymize

- Verifiera anonymisering
docker exec personregister-desktop python app.py check

- Radera all testdata
docker exec personregister-desktop python app.py clear
docker exec personregister-desktop python app.py check

- Stoppa Docker Desktop-läge
docker compose --profile desktop down


Detta gör det möjligt att inspektera applikationens beteende utan att starta om containern.

Resultat:

Containern stoppas och tas bort

Data som lagras i Docker-volymer bevaras

# Information

Docker Desktop-läget använder samma Docker-image och datavolym som standardläget

Ingen extra konfiguration krävs

Läget påverkar inte CI/CD eller automatiska tester

# När ska detta läge användas?

Visuell demonstration vid examination

Manuell kontroll av containerns livscykel

Visa start/stopp-beteende i Docker Desktop