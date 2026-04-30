# VoteSecure — Online Voting Platform

A full-stack online voting web application built with **Django 5.x**, **MySQL 8.4**, and **vanilla HTML/CSS/JavaScript**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![MySQL](https://img.shields.io/badge/MySQL-8.4-orange)

## Features

- **Secure Authentication** — Registration with email verification, login/logout
- **Election Management** — Admin can create, edit, schedule, and delete elections
- **Candidate Management** — Add/edit/remove candidates with photos and bios
- **One-Vote Enforcement** — Database-level unique constraint prevents double voting
- **Real-time Results** — Live Chart.js charts with auto-polling every 5 seconds
- **Admin Dashboard** — Stats overview, voter turnout, election management
- **Responsive Design** — Mobile-first dark theme with glassmorphism UI
- **Security** — CSRF protection, parameterized queries (ORM), session security, vote hashing

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + Django 5.2 |
| Database | MySQL 8.4 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js 4 |
| Auth | Django built-in + email verification |

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- Conda (or pip virtual environment)

## Setup & Installation

### 1. Clone & Activate Environment

```bash
cd online_voting
conda activate practice    # or your virtual environment
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file with your MySQL credentials:

```env
DB_NAME=online_voting_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 3. Create Database

```sql
CREATE DATABASE online_voting_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver 8080
```

Visit: **http://localhost:8080**

## Default Admin Credentials

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

## Project Structure

```
online_voting/
├── accounts/          # User auth app (registration, login, profiles)
├── elections/          # Core app (elections, candidates, voting, results)
├── templates/          # HTML templates
│   ├── accounts/       # Auth pages
│   ├── elections/      # Voter pages
│   └── admin_panel/    # Admin pages
├── static/            # CSS, JS, images
│   ├── css/style.css   # Design system
│   └── js/             # Frontend logic
├── online_voting/     # Django project settings
├── manage.py
├── requirements.txt
└── .env               # Environment config (gitignored)
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Set a strong `SECRET_KEY`
3. Configure SMTP email settings in `.env`
4. Run `python manage.py collectstatic`
5. Use Gunicorn: `gunicorn online_voting.wsgi:application --bind 0.0.0.0:8000`
6. Set up Nginx as reverse proxy
