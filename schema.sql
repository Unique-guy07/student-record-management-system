-- Student Record Management System schema
-- Run this script once in MySQL before starting the Flask application.

CREATE DATABASE IF NOT EXISTS student_records_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_records_db;

CREATE TABLE IF NOT EXISTS students (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    roll_no VARCHAR(30) NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(25) NULL,
    course VARCHAR(120) NOT NULL,
    year TINYINT UNSIGNED NOT NULL,
    date_of_birth DATE NULL,
    address VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_students_roll_no (roll_no),
    UNIQUE KEY uq_students_email (email),
    KEY idx_students_name (last_name, first_name),
    KEY idx_students_course (course),
    CONSTRAINT chk_students_year CHECK (year BETWEEN 1 AND 6)
) ENGINE=InnoDB;

-- Optional sample records for demonstration. Uncomment to use.
-- INSERT INTO students
-- (roll_no, first_name, last_name, email, phone, course, year, date_of_birth, address)
-- VALUES
-- ('CS-001', 'Aarav', 'Sharma', 'aarav@example.com', '9876543210',
--  'Computer Science', 2, '2005-04-12', 'Pune, Maharashtra');
