-- employees.sql

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    designation VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50)
);
