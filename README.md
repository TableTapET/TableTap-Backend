# TableTap-Backend
This repository serves for the backend for the web app.

## Tech Stack
- Framework: [Django](https://www.djangoproject.com/)
- Databases:
    - [MongoDB](https://www.mongodb.com/)
    - [SQLite](https://sqlite.org/)
- Language: [Python](https://www.typescriptlang.org/)

## Prerequisites
- [Python](https://www.python.org/downloads/) (v3.x or higher recommended)
- [Git](https://git-scm.com/downloads) (v2.x or higher recommended)

## Getting Started
1. **Clone this repository**:
    ```bash
    git clone https://github.com/TableTapET/TableTap-Backend.git
    cd TableTap-Backend
    ```
2. **Create [vitrual environment](https://docs.python.org/3/library/venv.html)**
   ```bash
   python -m venv .venv
   ```
3. **Activate virtual environment**
   > Once activated you should see something like this:
   >  - Windows: "(.venv) C:\<directory to project>\TableTap-Backend"
   >  - Mac\Linux: "(.venv) <username>@<device> TableTap-Backend"
   - Windows
     ```bash
     .venv\Scripts\activate.bat 
     ```
   - Mac/Linux
     ```bash
     source .venv/bin/activate
     ```
4. **Install dependencies to virtual environment**:
    ```
    pip install -r requirements.txt
    ```

## Usage(without docker)
> Running the backend locally will work, but it may not connect correctly with frontend.  
> If you want to run with docker, please use the [deployment setup instructions](https://github.com/TableTapET/TableTap-Deployment/blob/main/README.md) instead.
1. **Running the application locally**
    ```
    python manage.py migrate
    ```
    ```
    python manage.py runserver
    ```
2. The django server should now be running on:
    ```
    http://127.0.0.1:8000/
    ```

## Available Commands

- `python manage.py runserver` → Start the development server.
- `python manage.py migrate` → Initialize database.
- `python manage.py makemigrations` → Update database with new tables.
- `black .` → Fix any formatting errors.
- `isort . ` → Sort imports in project
