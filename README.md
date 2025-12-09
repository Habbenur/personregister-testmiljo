---
Projektet är skapat som en del av examinationsuppgift.
---

# Personregister i testmiljö

Detta projekt är ett enkelt personregister som används i en testmiljö.
Syftet är att visa hur testdata kan hanteras på ett GDPR-kompatibelt sätt.

## Teknisk översikt

Projektet är byggt med följande tekniker:

- Python – applikationslogik
- SQLite – enkel lokal databas
- Docker & Docker Compose – körning i isolerad miljö
- Git & GitHub – versionshantering

## Funktionalitet

Applikationen:

- Skapar en användartabell i en SQLite-databas
- Lägger till testanvändare om databasen är tom
- Visar alla användare
- Möjliggör anonymisering av användardata (GDPR)
- Möjliggör radering av all testdata (GDPR)

## Så här kör du projektet

### Förutsättningar

- Docker Desktop installerat och igång
- Git

### Starta applikationen med Docker

Kör följande kommando i projektets rotmapp:

#```bash
docker compose up --build
Applikationen startar då i en Docker-container och skapar en databas
med två testanvändare.

---

### GDPR-FUNKTIONER


### Anonymisering av användardata

Alla användares namn kan anonymiseras för att förhindra identifiering
av personuppgifter.

Kommando:

#```bash
docker exec gdpr-user-registry python -c "import app; app.anonymize_data(); app.display_users()"
Resultat:
Användarnamn ersätts med "Anonym Användare"
E-postadresser behålls för teständamål

---

### Radering av testdata

All testdata kan raderas helt i enlighet med GDPR:s principer
om rätten att bli bortglömd.

Kommando:

#```bash
docker exec gdpr-user-registry python -c "import app; app.clear_test_data(); app.display_users()"
Resultat:
Alla poster tas bort från databasen
Inga personuppgifter finns kvar

---

## GDPR-efterlevnad

Projektet följer GDPR-principer genom att:

- Använda testdata istället för produktionsdata
- Erbjuda anonymisering av personuppgifter
- Erbjuda fullständig radering av testdata
- Köra applikationen i en isolerad testmiljö

## CI/CD

Projektet använder GitHub Actions för automatisk kvalitetskontroll.
Vid varje push verifieras att koden kan köras och kompileras utan fel.

