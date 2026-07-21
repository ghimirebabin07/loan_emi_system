========== CREATE TABLES ==========

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    address VARCHAR(200)
);

CREATE TABLE loan_officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    branch VARCHAR(100)
);

CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    interest_rate DECIMAL(5,2) NOT NULL CHECK (interest_rate > 0),
    tenure_months INTEGER NOT NULL CHECK (tenure_months > 0),
    start_date DATE NOT NULL,
    customer_id INTEGER,
    officer_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (officer_id) REFERENCES loan_officers(id)
);

CREATE TABLE emi_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    due_date DATE NOT NULL,
    emi_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','paid','overdue','partially_paid')),
    loan_id INTEGER,
    FOREIGN KEY (loan_id) REFERENCES loans(id)
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paid_date DATE NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL CHECK (amount_paid > 0),
    payment_mode VARCHAR(30),
    emi_id INTEGER,
    FOREIGN KEY (emi_id) REFERENCES emi_schedule(id)
);


-- ========== INSERT SAMPLE DATA ==========

INSERT INTO customers (name, phone, address) VALUES
('Ram Thapa', '9800000001', 'Kathmandu'),
('Sita Gurung', '9800000002', 'Pokhara'),
('Hari Shrestha', '9800000003', 'Lalitpur'),
('Gita Rai', '9800000004', 'Bhaktapur'),
('Suresh Karki', '9800000005', 'Butwal');

INSERT INTO loan_officers (name, branch) VALUES
('Anil Bhattarai', 'Kathmandu Branch'),
('Manisha Adhikari', 'Pokhara Branch');

INSERT INTO loans (amount, interest_rate, tenure_months, start_date, customer_id, officer_id) VALUES
(50000, 12, 12, '2026-01-05', 1, 1),
(100000, 10, 24, '2026-02-10', 2, 1),
(30000, 14, 6, '2026-03-01', 3, 2),
(75000, 11, 18, '2026-01-20', 4, 2),
(20000, 13, 6, '2026-04-01', 5, 1);

INSERT INTO emi_schedule (due_date, emi_amount, status, loan_id) VALUES
('2026-02-05', 4442.44, 'paid', 1),
('2026-03-05', 4442.44, 'pending', 1),
('2026-03-10', 4614.49, 'paid', 2),
('2026-04-10', 4614.49, 'overdue', 2),
('2026-04-01', 5147.68, 'pending', 3),
('2026-02-20', 4325.90, 'paid', 4),
('2026-05-01', 3450.75, 'pending', 5);

INSERT INTO payments (paid_date, amount_paid, payment_mode, emi_id) VALUES
('2026-02-04', 4442.44, 'bank', 1),
('2026-03-09', 4614.49, 'cash', 3),
('2026-02-19', 4325.90, 'mobile wallet', 6);


-- ========== SELECT WITH WHERE ==========

-- All overdue EMIs
SELECT * FROM emi_schedule WHERE status = 'overdue';

-- All loans above a certain amount
SELECT * FROM loans WHERE amount > 50000;


-- ========== AGGREGATE + HAVING REPORT ==========

-- Customers with more than 1 loan
SELECT c.name, COUNT(l.id) AS total_loans
FROM customers c
JOIN loans l ON c.id = l.customer_id
GROUP BY c.name
HAVING COUNT(l.id) > 1;


-- ========== UPDATE ==========

-- Update a customer's phone number
UPDATE customers SET phone = '9811111111' WHERE id = 1;

-- Update an EMI status after payment
UPDATE emi_schedule SET status = 'paid' WHERE id = 5;


-- ========== DELETE (safely) ==========

-- Delete a payment record first (child row) before touching its parent
DELETE FROM payments WHERE id = 2;

-- Now it's safe to delete the EMI row it was attached to, if needed
-- (Always delete child rows before parent rows to avoid breaking FK links)


-- ========== INNER JOIN QUERIES (at least 3) ==========

-- 1. Loans with customer names
SELECT l.id AS loan_id, c.name AS customer_name, l.amount
FROM loans l
INNER JOIN customers c ON l.customer_id = c.id;

-- 2. EMI schedule with loan and customer info
SELECT e.id AS emi_id, e.due_date, e.status, c.name AS customer_name
FROM emi_schedule e
INNER JOIN loans l ON e.loan_id = l.id
INNER JOIN customers c ON l.customer_id = c.id;

-- 3. Payments with the customer who made them
SELECT p.id AS payment_id, p.amount_paid, c.name AS customer_name
FROM payments p
INNER JOIN emi_schedule e ON p.emi_id = e.id
INNER JOIN loans l ON e.loan_id = l.id
INNER JOIN customers c ON l.customer_id = c.id;