CREATE TABLE IF NOT EXISTS designation (
    id SERIAL ,
    designation VARCHAR(250) PRIMARY KEY,
    no_of_leaves INTEGER,
    UNIQUE (id , designation)
    );


CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255) ,
    designation VARCHAR(255) REFERENCES designation(designation),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS leaves (
    id SERIAL PRIMARY KEY ,
    employee_id INTEGER REFERENCES employees(id),
    leave_date DATE NOT NULL,
    reason VARCHAR(255),
    UNIQUE (employee_id,leave_date)
);

INSERT INTO designation (designation,no_of_leaves) VALUES ('system engineer' , 20),('senior engineer' , 18),('junior engineer' , 12),('Tech lead' , 12),('project manager' , 15);
