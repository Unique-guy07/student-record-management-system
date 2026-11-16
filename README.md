# Student Record Management System

A complete local Flask + MySQL web application for the DBMS assignment:

> Develop an application to demonstrate database connectivity with a relational database (SQL) using any suitable programming language.

This project demonstrates a browser-based application connected to MySQL through Flask and `mysql-connector-python`. It includes a dashboard, student CRUD operations, search, validation, parameterized SQL queries, and responsive Bootstrap pages.

## Features

- Dashboard with total student count, course count, database status, and recent records
- Add, view, search, edit, and delete student records
- Parameterized SQL queries for all user-supplied values
- MySQL schema with primary key, unique constraints, indexes, and a year check constraint
- Environment-based configuration through `.env`
- Responsive Bootstrap frontend with custom CSS
- Basic validation and friendly database/error handling

## Requirements

- Windows 10/11
- Python 3.10 or newer
- MySQL Server 8.0 or newer
- Visual Studio Code (recommended)

## Windows VS Code setup

### 1. Open the project

Extract or copy this folder, then open it in VS Code using **File → Open Folder**.

### 2. Create a virtual environment

Open the VS Code terminal (**Terminal → New Terminal**) and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in an administrator PowerShell window, or use Command Prompt instead:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Python packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the MySQL database and table

Start the MySQL service. In MySQL Workbench, open `schema.sql`, select all, and execute it. Alternatively, from a MySQL client:

```sql
SOURCE C:/full/path/to/student-record-management-system/schema.sql;
```

The script creates the `student_records_db` database and the `students` table. It does not insert sample data unless the optional insert is uncommented.

### 5. Configure the application

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set `MYSQL_USER`, `MYSQL_PASSWORD`, and any other values needed for your local MySQL installation. Do not commit `.env`; it is ignored by Git.

### 6. Run the application

```powershell
python app.py
```

Open http://127.0.0.1:5000 in a browser. Stop the server with `Ctrl+C`.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | development placeholder | Flask session and flash-message signing |
| `FLASK_DEBUG` | `0` | Enables Flask debug mode when set to `1` |
| `MYSQL_HOST` | `127.0.0.1` | MySQL server host |
| `MYSQL_PORT` | `3306` | MySQL server port |
| `MYSQL_DATABASE` | `student_records_db` | Database name |
| `MYSQL_USER` | `root` | MySQL username |
| `MYSQL_PASSWORD` | empty | MySQL password |

## Project structure

```text
student-record-management-system/
├── app.py                 # Flask routes, validation, and database operations
├── config.py              # Environment-based configuration
├── schema.sql             # MySQL database and table definition
├── requirements.txt       # Python dependencies
├── .env.example           # Configuration template
├── templates/             # Jinja2 HTML pages
│   ├── base.html
│   ├── dashboard.html
│   ├── students/
│   └── errors/
└── static/css/style.css   # Responsive custom styling
```

## DBMS concepts demonstrated

The application demonstrates database connectivity by opening a MySQL connection from Flask, executing SQL statements, fetching rows, committing changes, and closing resources. It uses:

- `CREATE DATABASE` and `CREATE TABLE`
- Primary and unique keys
- Indexes for search-related fields
- `SELECT`, `INSERT`, `UPDATE`, and `DELETE`
- `WHERE`, `LIKE`, `ORDER BY`, `COUNT`, `DISTINCT`, and `LIMIT`
- Parameterized placeholders (`%s`) to avoid SQL injection

## Notes and limitations

- Database operations are not claimed as tested in this delivery because a live MySQL server was not available in the build environment.
- The application gives a friendly error message if MySQL is stopped or the credentials are incorrect.
- Bootstrap and Google Fonts are loaded from CDNs while the application is running; for fully offline use, download and serve those assets locally.
- For production deployment, use a production WSGI server, a strong secret key, HTTPS, CSRF protection, and a restricted MySQL user rather than the root account.
