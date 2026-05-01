# Driving School Exam Minute Tracking

A small Django MVP for tracking weekly exam-minute pools for driving schools.

## Features

- Customer admins manage teachers and weekly minute pools for their own school.
- Teachers register used exam minutes and see the current week status.
- The service layer prevents overbooking with `transaction.atomic()`, `select_for_update()`, and `Sum` aggregation.
- School-scoped permissions keep each customer school isolated.
- SQLite works locally by default. PostgreSQL can be enabled with `DATABASE_URL`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000.

## Development Commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py test
```

## Notes

- Create schools and initial customer admin users through Django admin or the shell.
- Technical superusers can use Django admin regardless of school role.
- Customer-facing views require users to have a school assigned.
