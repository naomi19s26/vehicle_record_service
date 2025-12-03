# Vehicle API Service

A RESTful API for managing vehicle records with CRUD operations.

## Features
- Create, Read, Update, Delete vehicle information
- VIN validation (17 characters, case-insensitive)
- Comprehensive error handling
- PostgreSQL database with SQLite for testing

## Setup

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up PostgreSQL database (see Database Setup below)
6. Run: `python -m src.app` in vehicle_record_service directory

## Database Setup

CREATE DATABASE vehicle_db;
CREATE USER vehicle_service_user WITH PASSWORD 'vehicle_service_password';
GRANT ALL PRIVILEGES ON DATABASE vehicle_db TO vehicle_service_user;

## Running the application
python -m src.app

## Running Tests
pytest tests/ -v