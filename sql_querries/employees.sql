
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    designation VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS leaves (
    id SERIAL PRIMARY KEY ,
    employee_id INTEGER REFERENCES employees(id),
    leave_date DATE,
    reason VARCHAR(255),
    UNIQUE (employee_id,leave_date)
);


