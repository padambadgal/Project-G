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

            self.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute("PRAGMA journal_mode = WAL")

            self.create_tables()
            return True

        except sqlite3.Error as e:
            print("❌ Database Connection Error:", e)
            return False

    # ======================================================
    # CREATE TABLES (NEW CLEAN ARCHITECTURE)
    # ======================================================
    def create_tables(self):
        self.cursor.executescript("""
        
        -- =========================
        -- USERS TABLE
        -- =========================
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','doctor','patient')),
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            gender TEXT CHECK(gender IN ('Male','Female','Other')),
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- =========================
        -- PATIENT PROFILE
        -- =========================
        CREATE TABLE IF NOT EXISTS patient_profile (
            user_id INTEGER PRIMARY KEY,
            address TEXT,
            medical_history TEXT,
            emergency_contact TEXT,
            blood_group TEXT CHECK(
                blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')
            ),

            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- =========================
        -- DOCTOR PROFILE
        -- =========================
        CREATE TABLE IF NOT EXISTS doctor_profile (
            user_id INTEGER PRIMARY KEY,
            specialization TEXT NOT NULL,
            years_experience INTEGER,
            qualification TEXT,
            hospital_name TEXT,
            consultation_fee REAL,
            bio TEXT,
            available_days TEXT,
            available_time TEXT,

            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- =========================
        -- MEDICAL RECORDS
        -- =========================
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            symptoms TEXT,
            disease TEXT,
            diagnosis TEXT,
            prescription TEXT,
            notes TEXT,
            visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(patient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(doctor_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- =========================
        -- PREDICTIONS
        -- =========================
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            symptoms TEXT,
            predicted_disease TEXT,
            confidence REAL,
            risk_level TEXT CHECK(risk_level IN ('High','Medium','Low')),
            recommendation TEXT,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(patient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(doctor_id) REFERENCES users(id) ON DELETE SET NULL
        );

        -- =========================
        -- INDEXES
        -- =========================
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
        CREATE INDEX IF NOT EXISTS idx_patient_records ON medical_records(patient_id);
        CREATE INDEX IF NOT EXISTS idx_doctor_records ON medical_records(doctor_id);
        """)
        self.connection.commit()

    # ======================================================
    # QUERY METHODS
    # ======================================================
    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.connection.rollback()
            print("❌ Query Error:", e)
            print(query)
            return None

    def fetch_one(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print("Fetch Error:", e)
            return None

    def fetch_all(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Fetch Error:", e)
            return []

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()