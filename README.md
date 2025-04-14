# Wedding Invitations Website

A beautiful wedding invitation website with admin panel built with Django.

## Features
- Customizable wedding invitation templates
- RSVP management system
- Gallery section for couple photos
- Event details and location maps
- Admin panel for managing all content

## Installation

1. Install Python 3.8+ if not already installed
2. Install required packages:
```
pip install -r requirements.txt
```
3. Run migrations:
```
python manage.py migrate
```
4. Create a superuser for admin access:
```
python manage.py createsuperuser
```
5. Run the server:
```
python manage.py runserver
```
6. Access the admin panel at http://127.0.0.1:8000/admin/

## Admin Panel
The admin panel allows you to:
- Customize wedding details
- Manage guest list and RSVPs
- Upload photos to gallery
- Edit event schedule
- Customize website appearance
