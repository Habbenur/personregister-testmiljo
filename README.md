# Personregister – GDPR-anpassad testmiljö

> Projektet är skapat som en del av en examinationsuppgift.

Detta projekt demonstrerar hur personuppgifter kan hanteras säkert och kontrollerat i en testmiljö med hjälp av Docker, automatiserad anonymisering, enhetstester och CI/CD.

Fokus ligger på GDPR-anpassad hantering av testdata, inte på produktionssystem.

## Projektmål

- Skapa realistisk testdata med Faker
- Säkerställa att inga personuppgifter lämnas oavsiktligt oskyddade
- Tydligt separera: rå data, anonymisering, verifiering och radering
- Erbjuda ett reproducerbart arbetsflöde via Docker
- Validera funktionalitet automatiskt med tester och GitHub Actions

## Arkitekturöversikt

| | |
|---|---|
| Språk | Python 3.11 |
| Databas | SQLite |
| Testdatagenerering | Faker |
| Containerisering | Docker & Docker Compose |
| CI/CD | GitHub Actions |

Applikationen är medvetet enkel för att tydligt visa GDPR-relaterade designbeslut.

## GDPR – Anonymiserad testdata

**Hur fungerar det?**

1. Rå testdata skapas med Faker (namn, e-post, adress, personnummer-liknande värde)
2. Data anonymiseras explicit via ett separat kommando
3. En anonymiserings-guard säkerställer att ingen icke-anonym testdata lämnas kvar av misstag
4. Alla steg är spårbara, testbara och reproducerbara

### Anonymiseringsregler

| Fält | Anonymiserat värde |
|---|---|
| Namn | `Anonym Användare` |
| E-post | Hashat värde som slutar med `@anon.test` |
| Personnummer | `000000-0000` |
| Adress | `REDACTED` |

## Användning

Applikationen körs helt via Docker. Ingen lokal Python-installation krävs.

**Förutsättningar:** Docker, Docker Compose

**Bygg applikationen:**

```bash
docker compose build --no-cache
```

**Skapa rå testdata (Faker):**

Rå (icke-anonymiserad) testdata skapas endast explicit, för att tydligt kunna demonstrera skillnaden mellan rå och anonymiserad data:

```bash
docker compose run --rm app python app.py seed -n 5
```

**Lista lagrad data:**

```bash
docker compose run --rm app python app.py list
```

Före anonymisering visas realistisk testdata, efter anonymisering visas endast skyddade värden.

**Kontrollera anonymiseringsstatus (read-only):**

```bash
docker compose run --rm app python app.py check
```

Exempel på utdata: `total_test_rows=5 non_anonymized=5`. Kommandot ändrar aldrig data och fungerar som en revisions-/kontrollfunktion.

**Anonymisera testdata:**

```bash
docker compose run --rm app python app.py anonymize
```

**Radera all testdata (Right to Erasure – GDPR):**

```bash
docker compose run --rm app python app.py clear
```

Detta tar permanent bort all testdata från databasen.

**Köra automatiska tester:**

```bash
docker compose run --rm app python app.py --test
```

Testerna verifierar skapande av testdata, anonymiseringslogik, guard-beteende och dataintegritet.

## CI/CD

GitHub Actions kör automatiskt alla enhetstester vid varje push och varje pull request:

```yaml
on: [push, pull_request]
```

Testerna verifierar att:

- testdata kan skapas korrekt
- anonymisering fungerar som förväntat
- ingen icke-anonymiserad testdata lämnas kvar
- applikationen kan köras utan fel

Om något test misslyckas markeras bygget som misslyckat, vilket förhindrar att felaktig kod går vidare. Samma testsvit används lokalt och i CI, vilket säkerställer långsiktig kvalitet och GDPR-efterlevnad.

## Demonstrerade GDPR-principer

- Dataminimering
- Explicit anonymisering
- Spårbarhet och kontroll (read-only checks)
- Rätten att bli raderad (Right to Erasure)
- Automatisering och reproducerbarhet

## Designbeslut

- Anonymisering är explicit, inte implicit
- Kontrollkommandon ändrar aldrig data
- Radering är oåterkallelig
- Testdata hålls strikt åtskild från produktionslogik
- Docker används för att skapa en kontrollerad och inspekterbar miljö

## Docker Desktop – visuellt demonstrationsläge

Projektet stöder även ett Docker Desktop-läge för visuell demonstration och manuell hantering av containerns livscykel, avsett för demonstration och examination.

**Starta Docker Desktop-läge** (från projektets rotkatalog):

```bash
docker compose --profile desktop up -d
```

Detta startar en långlivad container med namnet `personregister-desktop`, synlig i Docker Desktop och möjlig att starta/stoppa manuellt därifrån.

**Verifiera att containern körs:**

```bash
docker ps
```

Förväntat resultat: `personregister-desktop   Up ...`

**Full demonstrationssekvens:**

```bash
# Starta Docker Desktop-läge
docker compose --profile desktop up -d

# Skapa rå testdata
docker exec personregister-desktop python app.py seed -n 5

# Visa rå data
docker exec personregister-desktop python app.py list

# Kontrollera (icke-anonymiserad data)
docker exec personregister-desktop python app.py check

# Anonymisera data
docker exec personregister-desktop python app.py anonymize

# Verifiera anonymisering
docker exec personregister-desktop python app.py check

# Radera all testdata
docker exec personregister-desktop python app.py clear
docker exec personregister-desktop python app.py check

# Stoppa Docker Desktop-läge
docker compose --profile desktop down
```

Stoppar och tar bort containern; data som lagras i Docker-volymer bevaras.

**Information:**

- Docker Desktop-läget använder samma Docker-image och datavolym som standardläget
- Ingen extra konfiguration krävs
- Läget påverkar inte CI/CD eller automatiska tester

**När ska detta läge användas?**

- Visuell demonstration vid examination
- Manuell kontroll av containerns livscykel
- Visa start/stopp-beteende i Docker Desktop

---

Projektet visar ett rent, testbart och GDPR-medvetet arbetssätt för hantering av personuppgifter i utvecklings- och testmiljöer med moderna verktyg och bästa praxis.
