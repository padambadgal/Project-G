import sqlite3
import os
from config.settings import DB_PATH


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Create database connection"""

        try:
            # Create database directory
            database_dir = os.path.dirname(DB_PATH)

            if database_dir:
                os.makedirs(database_dir, exist_ok=True)

            self.connection = sqlite3.connect(DB_PATH)

            # Return rows like dictionaries
            self.connection.row_factory = sqlite3.Row

            self.cursor = self.connection.cursor()

            # Enable foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")

            # Create tables
            self.create_tables()

            print("Database Connected Successfully.")

            return True

        except sqlite3.Error as e:
            print(f"Database Connection Error: {e}")
            return False

    def create_tables(self):
        """Create all required tables"""

        # ---------------- USERS ---------------- #

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL,

            full_name TEXT NOT NULL,

            email TEXT UNIQUE,

            phone TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ---------------- PATIENTS ---------------- #

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id TEXT UNIQUE NOT NULL,

            full_name TEXT NOT NULL,

            age INTEGER,

            gender TEXT,

            contact TEXT,

            address TEXT,

            medical_history TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ---------------- DOCTORS ---------------- #

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            doctor_id TEXT UNIQUE NOT NULL,

            full_name TEXT NOT NULL,

            specialization TEXT,

            contact TEXT,

            email TEXT UNIQUE,

            years_experience INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ---------------- PREDICTIONS ---------------- #

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id TEXT NOT NULL,

            doctor_id TEXT,

            symptoms TEXT,

            predicted_disease TEXT,

            confidence REAL,

            risk_level TEXT,

            recommendation TEXT,

            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(patient_id)
                REFERENCES patients(patient_id)
                ON DELETE CASCADE,

            FOREIGN KEY(doctor_id)
                REFERENCES doctors(doctor_id)
                ON DELETE SET NULL
        )
        """)

        self.connection.commit()

    # ==================================================
    # INSERT / UPDATE / DELETE
    # ==================================================

    def execute_query(self, query, params=()):
        """
        Execute INSERT, UPDATE, DELETE
        """

        try:

            self.cursor.execute(query, params)

            self.connection.commit()

            return self.cursor.lastrowid

        except sqlite3.Error as e:

            self.connection.rollback()

            print(f"Database Error: {e}")

            return None

    # ==================================================
    # SELECT ALL
    # ==================================================

    def fetch_all(self, query, params=()):

        try:

            self.cursor.execute(query, params)

            return self.cursor.fetchall()

        except sqlite3.Error as e:

            print(f"Fetch Error: {e}")

            return []

    # ==================================================
    # SELECT ONE
    # ==================================================

    def fetch_one(self, query, params=()):

        try:

            self.cursor.execute(query, params)

            return self.cursor.fetchone()

        except sqlite3.Error as e:

            print(f"Fetch Error: {e}")

            return None

    # ==================================================
    # CHECK RECORD EXISTS
    # ==================================================

    def exists(self, query, params=()):

        result = self.fetch_one(query, params)

        return result is not None

    # ==================================================
    # GET ROW COUNT
    # ==================================================

    def count(self, table):

        try:

            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")

            return self.cursor.fetchone()[0]

        except sqlite3.Error:

            return 0

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):

        if self.connection:

            self.connection.close()

            print("Database Closed.")

    # ==================================================
    # CONTEXT MANAGER
    # ==================================================

    def __enter__(self):

        self.connect()

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.close()