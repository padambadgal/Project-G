# database/database.py
import os
import sqlite3
from config.settings import DB_PATH


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    # ======================================================
    # CONNECT
    # ======================================================

    def connect(self):
        if self.connection:
            return True

        try:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

            # ✅ ADD THIS: Allow multi-thread access
            self.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute("PRAGMA journal_mode=WAL")
            self.cursor.execute("PRAGMA synchronous=NORMAL")

            self.create_tables()
            return True

        except sqlite3.Error as e:
            print("Database Connection Error:", e)
            return False

    # ======================================================
    # CREATE TABLES
    # ======================================================

    def create_tables(self):
        self.cursor.executescript("""
        
        -- ============================================
        -- SINGLE USER TABLE - All users in one table
        -- ============================================
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            
            -- Common fields
            gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
            age INTEGER CHECK(age >= 0 AND age <= 150),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Doctor specific fields (NULL for non-doctors)
            specialization TEXT,
            years_experience INTEGER CHECK(years_experience >= 0),
            
            -- Patient specific fields (NULL for non-patients)
            medical_history TEXT,
            emergency_contact TEXT,
            blood_group TEXT CHECK(blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'))
        );

        -- ============================================
        -- PREDICTIONS TABLE
        -- ============================================
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            symptoms TEXT,
            predicted_disease TEXT,
            confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
            risk_level TEXT CHECK(risk_level IN ('High', 'Medium', 'Low')),
            recommendation TEXT,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY(patient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(doctor_id) REFERENCES users(id) ON DELETE SET NULL
        );

        -- ============================================
        -- INDEXES
        -- ============================================
        CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_predictions_patient ON predictions(patient_id);
        CREATE INDEX IF NOT EXISTS idx_predictions_doctor ON predictions(doctor_id);
        
        """)
        self.connection.commit()

    # ======================================================
    # QUERY METHODS
    # ======================================================

    def execute_query(self, query, params=()):
        
    try:
        print(f"🔍 DEBUG: Executing query: {query[:100]}...")
        print(f"🔍 DEBUG: Params: {params}")
        
        self.cursor.execute(query, params)
        self.connection.commit()
        
        # Check if it was an INSERT
        if query.strip().upper().startswith('INSERT'):
            last_id = self.cursor.lastrowid
            print(f"🔍 DEBUG: Last row ID: {last_id}")
            
            # If lastrowid is 0, try to get it differently
            if last_id == 0:
                # Get the last inserted ID
                self.cursor.execute("SELECT last_insert_rowid()")
                last_id = self.cursor.fetchone()[0]
                print(f"🔍 DEBUG: Last insert rowid from query: {last_id}")
            
            return last_id
        else:
            rows_affected = self.cursor.rowcount
            print(f"🔍 DEBUG: Rows affected: {rows_affected}")
            return rows_affected
            
    except sqlite3.Error as e:
        self.connection.rollback()
        print(f"❌ Database Error: {e}")
        print(f"❌ Query: {query}")
        print(f"❌ Params: {params}")
        return None

    def fetch_all(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Fetch Error:", e)
            return []

    def fetch_one(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print("Fetch Error:", e)
            return None

    def exists(self, query, params=()):
        return self.fetch_one(query, params) is not None

    def count(self, table):
        try:
            row = self.fetch_one(f"SELECT COUNT(*) AS total FROM {table}")
            return row["total"] if row else 0
        except sqlite3.Error:
            return 0

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()