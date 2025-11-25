
# Provent CRM Backend (PostgreSQL / Render)

בקאנד נקי ל-CRM של פרובנט, מותאם למסד PostgreSQL ב-Render.

## Environment variables

DATABASE_URL=postgresql://proventadmin:...@dpg-.../proventcrm
JWT_SECRET_KEY=משהו_סודי_שלך
FRONTEND_ORIGIN=https://crm.pro-net.pro
UPLOAD_FOLDER=/mnt/uploads

## Render

* Build command: pip install -r requirements.txt
* Start command: gunicorn app:app
