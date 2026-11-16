"""Student Record Management System.

Flask web application backed by MySQL.  All values supplied by users are sent
to MySQL through parameterized queries.
"""

from datetime import date
import re

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, url_for
from mysql.connector import Error

from config import Config


app = Flask(__name__)
app.config.from_object(Config)


def get_db_connection():
    """Open a MySQL connection using values loaded from environment variables."""
    return mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        port=app.config["MYSQL_PORT"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DATABASE"],
    )


def fetch_one(query, params=()):
    """Run a parameterized SELECT that returns one row as a dictionary."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def fetch_all(query, params=()):
    """Run a parameterized SELECT that returns rows as dictionaries."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def execute_write(query, params=()):
    """Run a parameterized INSERT, UPDATE, or DELETE and commit it."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        return cursor.lastrowid, cursor.rowcount
    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def clean_form_data(form):
    """Normalize form values before validation and database persistence."""
    return {
        "roll_no": form.get("roll_no", "").strip(),
        "first_name": form.get("first_name", "").strip(),
        "last_name": form.get("last_name", "").strip(),
        "email": form.get("email", "").strip().lower(),
        "phone": form.get("phone", "").strip(),
        "course": form.get("course", "").strip(),
        "year": form.get("year", "").strip(),
        "date_of_birth": form.get("date_of_birth", "").strip(),
        "address": form.get("address", "").strip(),
    }


def validate_student(data):
    """Return a field-error dictionary for student form data."""
    errors = {}
    required_fields = {
        "roll_no": "Roll number is required.",
        "first_name": "First name is required.",
        "last_name": "Last name is required.",
        "email": "Email is required.",
        "course": "Course is required.",
        "year": "Year is required.",
    }
    for field, message in required_fields.items():
        if not data[field]:
            errors[field] = message

    if data["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", data["email"]):
        errors["email"] = "Enter a valid email address."

    if data["year"]:
        try:
            year = int(data["year"])
            if year < 1 or year > 6:
                errors["year"] = "Year must be between 1 and 6."
        except ValueError:
            errors["year"] = "Year must be a whole number."

    if data["date_of_birth"]:
        try:
            dob = date.fromisoformat(data["date_of_birth"])
            if dob > date.today():
                errors["date_of_birth"] = "Date of birth cannot be in the future."
        except ValueError:
            errors["date_of_birth"] = "Enter a valid date of birth."

    if len(data["roll_no"]) > 30:
        errors["roll_no"] = "Roll number must be 30 characters or fewer."
    if len(data["address"]) > 500:
        errors["address"] = "Address must be 500 characters or fewer."
    return errors


@app.route("/")
def dashboard():
    """Display summary counts and the latest student records."""
    try:
        total = fetch_one("SELECT COUNT(*) AS total FROM students")["total"]
        courses = fetch_one("SELECT COUNT(DISTINCT course) AS total FROM students")["total"]
        recent_students = fetch_all(
            """SELECT id, roll_no, first_name, last_name, course, year
               FROM students ORDER BY created_at DESC, id DESC LIMIT 5"""
        )
        return render_template(
            "dashboard.html", total=total, courses=courses, recent_students=recent_students
        )
    except Error as error:
        app.logger.exception("Dashboard database error: %s", error)
        flash("The database is unavailable. Check your MySQL settings and try again.", "danger")
        return render_template("dashboard.html", total=None, courses=None, recent_students=[])


@app.route("/students")
def list_students():
    """List all students or filter by a search term."""
    search = request.args.get("q", "").strip()
    like_value = f"%{search}%"
    query = """SELECT id, roll_no, first_name, last_name, email, phone, course, year,
                      date_of_birth, address, created_at, updated_at
               FROM students
               WHERE roll_no LIKE %s OR first_name LIKE %s OR last_name LIKE %s
                     OR email LIKE %s OR course LIKE %s
               ORDER BY last_name, first_name, id"""
    try:
        students = fetch_all(query, (like_value,) * 5)
        return render_template("students/list.html", students=students, search=search)
    except Error as error:
        app.logger.exception("Student list database error: %s", error)
        flash("Unable to load student records right now.", "danger")
        return render_template("students/list.html", students=[], search=search)


@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    """Display and process the create-student form."""
    data = clean_form_data(request.form) if request.method == "POST" else {}
    errors = validate_student(data) if request.method == "POST" else {}

    if request.method == "POST" and not errors:
        try:
            execute_write(
                """INSERT INTO students
                   (roll_no, first_name, last_name, email, phone, course, year,
                    date_of_birth, address)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NULLIF(%s, ''), %s)""",
                (
                    data["roll_no"], data["first_name"], data["last_name"], data["email"],
                    data["phone"], data["course"], int(data["year"]),
                    data["date_of_birth"], data["address"],
                ),
            )
            flash("Student record added successfully.", "success")
            return redirect(url_for("list_students"))
        except mysql.connector.IntegrityError:
            errors["roll_no"] = "That roll number or email already exists."
        except Error as error:
            app.logger.exception("Add student database error: %s", error)
            flash("Unable to save the student record.", "danger")

    return render_template("students/form.html", student=data, errors=errors, mode="Add")


@app.route("/students/<int:student_id>")
def student_detail(student_id):
    """Show one student record."""
    try:
        student = fetch_one("SELECT * FROM students WHERE id = %s", (student_id,))
        if not student:
            return render_template("errors/404.html"), 404
        return render_template("students/detail.html", student=student)
    except Error as error:
        app.logger.exception("Student detail database error: %s", error)
        flash("Unable to load that student record.", "danger")
        return redirect(url_for("list_students"))


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    """Display and process the edit-student form."""
    try:
        existing = fetch_one("SELECT * FROM students WHERE id = %s", (student_id,))
    except Error as error:
        app.logger.exception("Edit student lookup error: %s", error)
        flash("Unable to load that student record.", "danger")
        return redirect(url_for("list_students"))

    if not existing:
        return render_template("errors/404.html"), 404

    if request.method == "POST":
        data = clean_form_data(request.form)
        errors = validate_student(data)
        if not errors:
            try:
                execute_write(
                    """UPDATE students SET roll_no=%s, first_name=%s, last_name=%s,
                       email=%s, phone=%s, course=%s, year=%s,
                       date_of_birth=NULLIF(%s, ''), address=%s
                       WHERE id=%s""",
                    (
                        data["roll_no"], data["first_name"], data["last_name"], data["email"],
                        data["phone"], data["course"], int(data["year"]),
                        data["date_of_birth"], data["address"], student_id,
                    ),
                )
                flash("Student record updated successfully.", "success")
                return redirect(url_for("student_detail", student_id=student_id))
            except mysql.connector.IntegrityError:
                errors["roll_no"] = "That roll number or email already exists."
            except Error as error:
                app.logger.exception("Edit student database error: %s", error)
                flash("Unable to update the student record.", "danger")
        return render_template("students/form.html", student=data, errors=errors, mode="Edit")

    return render_template("students/form.html", student=existing, errors={}, mode="Edit")


@app.post("/students/<int:student_id>/delete")
def delete_student(student_id):
    """Delete one student record after a confirmation in the browser."""
    try:
        _, affected_rows = execute_write("DELETE FROM students WHERE id = %s", (student_id,))
        if affected_rows:
            flash("Student record deleted.", "success")
        else:
            flash("Student record was not found.", "warning")
    except Error as error:
        app.logger.exception("Delete student database error: %s", error)
        flash("Unable to delete the student record.", "danger")
    return redirect(url_for("list_students"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
