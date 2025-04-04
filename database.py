import streamlit as st
import pandas as pd
import os
import json
import sqlite3
import csv
import bcrypt
from pathlib import Path
from io import StringIO
from collections import defaultdict
from datetime import datetime

# Constants
DB_FILE = 'kupuna.db'

@st.cache_resource
def load_exercise_data():
    """Load exercise data from environment variable"""
    try:
        exercises = os.getenv("EXERCISES", "{}")
        return json.loads(exercises)
    except (json.JSONDecodeError, TypeError) as e:
        st.error(f"Error loading exercise data: {e}")
        return {}

def get_connection():
    """Create and return a database connection, creating the db file if needed"""
    try:
        db_path = Path(DB_FILE)
        db_path.touch(exist_ok=True)  # Create file if it doesn't exist
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

@st.cache_resource
def initialize_database():
    """
    Initialize the SQLite database and create tables if they don't exist.
    Returns True if successful, False otherwise.
    """
    try:
        conn = get_connection()
        if conn is None:
            return False

        cursor = conn.cursor()

        # Define complete database schema
        schema = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobility TEXT NOT NULL,
            length TEXT NOT NULL,
            phase TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            video TEXT
        );
        
        CREATE TABLE IF NOT EXISTS routines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            music TEXT
        );
        
        CREATE TABLE IF NOT EXISTS routine_exercises (
            routine_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            FOREIGN KEY (routine_id) REFERENCES routines(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id),
            PRIMARY KEY (routine_id, exercise_id)
        );
        
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            race TEXT
        );
        
        CREATE TABLE IF NOT EXISTS patient_routines (
            patient_id INTEGER NOT NULL,
            routine_id INTEGER NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (routine_id) REFERENCES routines(id),
            PRIMARY KEY (patient_id, routine_id)
        );
        
        CREATE TABLE IF NOT EXISTS exercise_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            routine_id INTEGER NOT NULL,
            date_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            mood_level INTEGER,
            comments TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (routine_id) REFERENCES routines(id)
        );
        """

        # Execute schema creation
        cursor.executescript(schema)
        conn.commit()

        # Check if exercises table is empty
        cursor.execute("SELECT COUNT(*) FROM exercises")
        exercise_count = cursor.fetchone()[0]

        # Insert initial data if tables are empty
        if exercise_count == 0:
            # Insert exercise data
            exercise_data = load_exercise_data()
            if exercise_data:
                for mobility, lengths in exercise_data.items():
                    for length, phases in lengths.items():
                        for phase, exercises in phases.items():
                            for exercise in exercises:
                                cursor.execute('''
                                    INSERT INTO exercises (mobility, length, phase, name, description, video)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (mobility, length, phase, 
                                      exercise.get('name', ''),
                                      exercise.get('description', ''),
                                      exercise.get('video', '')))

            # Insert test users if provided
            users = os.getenv("USERS", "")
            if users:
                try:
                    csv_reader = csv.DictReader(StringIO(users))
                    for row in csv_reader:
                        hashed_pw = bcrypt.hashpw(row['password'].encode(), bcrypt.gensalt())
                        cursor.execute('''
                            INSERT INTO users (username, password, role)
                            VALUES (?, ?, ?)
                        ''', (row['username'], hashed_pw, row.get('role', 'user')))
                except Exception as e:
                    st.warning(f"Couldn't insert test users: {e}")

            conn.commit()

        return True

    except sqlite3.Error as e:
        st.error(f"Database initialization failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

@st.cache_data
def get_all_exercises():
    """Fetch all exercises from database"""
    try:
        conn = get_connection()
        if conn is None:
            return {}

        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, mobility, length, phase, name, description, video
            FROM exercises
        ''')

        rows = cursor.fetchall()
        exercise_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for row in rows:
            exercise = {
                "id": row['id'],
                "name": row['name'],
                "description": row['description'],
                "video": row['video']
            }
            exercise_data[row['mobility']][row['length']][row['phase']].append(exercise)

        return dict(exercise_data)
    except sqlite3.Error as e:
        st.error(f"Error fetching exercises: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def insert_routine(routine_name, description, music, exercise_ids):
    """Insert a new routine with associated exercises"""
    try:
        conn = get_connection()
        if conn is None:
            return False

        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO routines (name, description, music)
        VALUES (?, ?, ?)
        ''', (routine_name, description, music))

        routine_id = cursor.lastrowid

        for exercise_id in exercise_ids:
            cursor.execute('''
            INSERT INTO routine_exercises (routine_id, exercise_id)
            VALUES (?, ?)
            ''', (routine_id, exercise_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error inserting routine: {e}")
        return False
    finally:
        if conn:
            conn.close()

# [Rest of your functions with similar error handling...]

def assign_patient_to_routine(patient_id, routine_id):
    """Assign a routine to a patient"""
    try:
        conn = get_connection()
        if conn is None:
            return False

        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO patient_routines (patient_id, routine_id)
        VALUES (?, ?)
        ''', (patient_id, routine_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error assigning routine: {e}")
        return False
    finally:
        if conn:
            conn.close()

def insert_exercise_log(patient_id, routine_id, date_time, duration_minutes, mood_level, comments=None):
    """Log an exercise session"""
    try:
        conn = get_connection()
        if conn is None:
            return False

        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO exercise_logs (patient_id, routine_id, date_time, duration_minutes, mood_level, comments)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (patient_id, routine_id, date_time, duration_minutes, mood_level, comments))

        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error logging exercise: {e}")
        return False
    finally:
        if conn:
            conn.close()

def fetch_patients():
    """Fetch all patients"""
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()

        query = """
        SELECT id, name, age, gender, race
        FROM patients
        """
        return pd.read_sql(query, conn)
    except sqlite3.Error as e:
        st.error(f"Error fetching patients: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def fetch_routines():
    """Fetch all routines"""
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()

        query = """
        SELECT id, name, description, music
        FROM routines
        """
        return pd.read_sql(query, conn)
    except sqlite3.Error as e:
        st.error(f"Error fetching routines: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def fetch_patient_routines():
    """Fetch all patient-routine assignments"""
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()

        query = """
        SELECT pr.patient_id, pr.routine_id, p.name AS patient_name, r.name AS routine_name
        FROM patient_routines pr
        JOIN patients p ON pr.patient_id = p.id
        JOIN routines r ON pr.routine_id = r.id
        """
        return pd.read_sql(query, conn)
    except sqlite3.Error as e:
        st.error(f"Error fetching patient routines: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def fetch_exercise_logs(patient_id, routine_id):
    """Fetch exercise logs for a patient and routine"""
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()

        query = """
        SELECT date_time, duration_minutes, mood_level, comments
        FROM exercise_logs
        WHERE patient_id = ? AND routine_id = ?
        ORDER BY date_time
        """
        return pd.read_sql(query, conn, params=(patient_id, routine_id))
    except sqlite3.Error as e:
        st.error(f"Error fetching exercise logs: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

@st.cache_data
def get_exercises_for_routine(routine_id):
    """Get exercises for a specific routine"""
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()

        query = """
        SELECT e.name, e.description, e.phase, e.video
        FROM exercises e
        JOIN routine_exercises re ON e.id = re.exercise_id
        WHERE re.routine_id = ?
        ORDER BY e.phase
        """
        return pd.read_sql(query, conn, params=(routine_id,))
    except sqlite3.Error as e:
        st.error(f"Error fetching routine exercises: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def add_user(username, password, role="user"):
    """Add a new user to the database"""
    try:
        conn = get_connection()
        if conn is None:
            return False

        cursor = conn.cursor()
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, (username, hashed_pw, role))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error adding user: {e}")
        return False
    finally:
        if conn:
            conn.close()

@st.cache_data
def get_user(username):
    """Get user by username"""
    try:
        conn = get_connection()
        if conn is None:
            return None

        query = """
        SELECT username, password, role 
        FROM users 
        WHERE username = ?
        """
        df = pd.read_sql(query, conn, params=(username,))
        return df.iloc[0] if not df.empty else None
    except sqlite3.Error as e:
        st.error(f"Error fetching user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def bulk_insert_patient(df):
    """Bulk insert patients from DataFrame"""
    try:
        conn = get_connection()
        if conn is None:
            return False

        mapped_df = df[["NAME", "MEM_AGE", "MEM_GENDER", "MEM_RACE"]].rename(
            columns={
                "NAME": "name",
                "MEM_AGE": "age",
                "MEM_GENDER": "gender",
                "MEM_RACE": "race"
            }
        )

        mapped_df.to_sql("patients", conn, if_exists="append", index=False)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error bulk inserting patients: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_exercise_stats(patient_id, routine_id):
    """Get exercise statistics for a patient"""
    try:
        conn = get_connection()
        if conn is None:
            return 0, 0

        cursor = conn.cursor()
        query = """
        SELECT date_time 
        FROM exercise_logs
        WHERE patient_id = ? AND routine_id = ?
        ORDER BY date_time
        """
        
        cursor.execute(query, (patient_id, routine_id))
        rows = cursor.fetchall()

        if not rows:
            return 0, 0
        
        dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in rows]
        streaks = []
        current_streak = 1

        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1
        streaks.append(current_streak)

        return len(dates), max(streaks)
    except sqlite3.Error as e:
        st.error(f"Error getting exercise stats: {e}")
        return 0, 0
    finally:
        if conn:
            conn.close()
