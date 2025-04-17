# IT Helpdesk

A comprehensive internal IT helpdesk ticketing application built with Flask and MySQL.

## Features

- User authentication and authorization
- Ticket submission with file attachments
- Ticket management and tracking
- Internal notes and comments
- Email notifications
- Role-based access control
- Responsive web interface

## Requirements

- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)
- Gunicorn (for production)
- Nginx (recommended for production)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rahmanekm/helpdesk.git
cd helpdesk
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
. .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode
For development purposes, you can use Flask's built-in development server:
```bash
flask run
```
The application will be available at `http://localhost:5000`

### Production Mode
For production deployment, it's recommended to use Gunicorn with Nginx:

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

3. Configure Nginx as a reverse proxy (recommended for production):
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables
Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://username:password@localhost/helpdesk
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password
```
