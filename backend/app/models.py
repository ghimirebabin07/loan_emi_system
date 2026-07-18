def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_officers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK (amount > 0),
            interest_rate REAL NOT NULL CHECK (interest_rate > 0),
            tenure_months INTEGER NOT NULL CHECK (tenure_months > 0),
            start_date TEXT NOT NULL,
            customer_id INTEGER,
            officer_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (officer_id) REFERENCES loan_officers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emi_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            due_date TEXT NOT NULL,
            emi_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','paid','overdue','partially_paid')),
            loan_id INTEGER,
            FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paid_date TEXT NOT NULL,
            amount_paid REAL NOT NULL CHECK (amount_paid > 0),
            payment_mode TEXT,
            emi_id INTEGER,
            FOREIGN KEY (emi_id) REFERENCES emi_schedule(id)
        )
    """)

    conn.commit()