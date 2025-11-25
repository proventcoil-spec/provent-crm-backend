# Provent CRM - Core Backend (Clean Version)

זהו בקאנד חדש, נקי ומודרני לקרם של פרובנט:

* Flask + SQLAlchemy
* JWT Authentication
* מודלים ל-Users, Clients, Events, Leads, MediaFiles, Contracts
* API בסיסי ל:
  * /api/auth/login
  * /api/clients
  * /api/events
  * /api/leads
  * /api/uploads/event/<id>/files

## Environment variables

DATABASE_URL או DB_HOST / DB_USER / DB_PASS / DB_NAME

JWT_SECRET_KEY=Provent-Secret-2025
FRONTEND_ORIGIN=https://crm.pro-net.pro
UPLOAD_FOLDER=/mnt/uploads

## Run (local)

pip install -r requirements.txt
flask --app app run
