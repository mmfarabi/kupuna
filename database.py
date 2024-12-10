import streamlit as st
import pandas as pd
import os
import json
import sqlite3
import csv
import bcrypt

from io import StringIO
from collections import defaultdict

@st.cache_resource
def load_exercise_data():
    return json.loads(os.getenv("EXERCISES"))

def get_connection():
    conn = sqlite3.connect('kupuna.db')
    return conn

@st.cache_resource
def initialize_database():
    """
    Initialize the SQLite database and create the table if it doesn't exist.
    Ensures initialization runs only once per session.
    """
    if "db_initialized" not in st.session_state:
        # Load database URL from TOML config
        conn = get_connection()
        cursor = conn.cursor()

        schema = os.getenv("SCHEMA_SQL")
        cursor.executescript(schema)
        
        exercise_data = load_exercise_data()
        # Insert data into the database
        for mobility, lengths in exercise_data.items():
            for length, phases in lengths.items():
                for phase, exercises in phases.items():
                    for exercise in exercises:
                        cursor.execute('''
                            INSERT INTO exercises (mobility, length, phase, name, description, video)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (mobility, length, phase, exercise['name'], exercise['description'], exercise['video']))

        # Insert test users
        users = os.getenv("USERS")
        csv_reader = csv.DictReader(StringIO(users))
        for row in csv_reader:
            try:
                cursor.execute('''
                    INSERT INTO users (username, password, role)
                    VALUES (?, ?, ?)
                ''', (row['username'], bcrypt.hashpw(row['password'].encode(), bcrypt.gensalt()), row['role']))
            except:
                continue
          
        conn.commit()
        conn.close()
        st.session_state["db_initialized"] = True  # Mark initialization as complete

@st.cache_data
def get_all_exercises():
    # Connect to the SQLite database
    conn = get_connection()
    cursor = conn.cursor()

    # Query to fetch all data
    cursor.execute('''
        SELECT id, mobility, length, phase, name, description, video
        FROM exercises
    ''')

    # Fetch all results from the query
    rows = cursor.fetchall()

    # Create a nested dictionary structure
    exercise_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for row in rows:
        id, mobility, length, phase, name, description, video = row
        exercise = {
            "id": id,
            "name": name,
            "description": description,
            "video": video
        }
        exercise_data[mobility][length][phase].append(exercise)

    # Convert defaultdict to a standard dictionary
    exercise_data = {k: {kk: dict(vv) for kk, vv in v.items()} for k, v in exercise_data.items()}

    # Close the database connection
    conn.close()

    # Return the exercises dictionary
    return exercise_data

def insert_routine(routine_name, description, music, exercise_ids):
    # Connect to SQLite database
    conn = get_connection()
    cursor = conn.cursor()

    # Insert routine into the 'routines' table
    cursor.execute('''
    INSERT INTO routines (name, description, music)
    VALUES (?, ?, ?)
    ''', (routine_name, description, music))

    # Get the ID of the newly inserted routine
    routine_id = cursor.lastrowid

    # Insert each exercise into the 'routine_exercises' table
    for exercise_id in exercise_ids:
        cursor.execute('''
        INSERT INTO routine_exercises (routine_id, exercise_id)
        VALUES (?, ?)
        ''', (routine_id, exercise_id))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def assign_patient_to_routine(patient_id, routine_id):
    # Connect to the SQLite database
    conn = get_connection()
    cursor = conn.cursor()

    # Insert the patient-routine relationship into the patient_routines table
    cursor.execute('''
    INSERT OR REPLACE INTO patient_routines (patient_id, routine_id)
    VALUES (?, ?)
    ''', (patient_id, routine_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_exercise_log(patient_id, routine_id, date_time, duration_minutes, mood_level, comments=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO exercise_logs (patient_id, routine_id, date_time, duration_minutes, mood_level, comments)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (patient_id, routine_id, date_time, duration_minutes, mood_level, comments))

    conn.commit()
    conn.close()

def fetch_patients():
    conn = get_connection()
    query = """
    SELECT id, name, age, gender, ethnicity
    FROM patients
    """
    patients = pd.read_sql(query, conn)
    conn.close()
    return patients

def fetch_routines():
    conn = get_connection()
    query = """
    SELECT id, name, description, music
    FROM routines
    """
    routines = pd.read_sql(query, conn)
    conn.close()
    return routines

def fetch_patient_routines():
    conn = get_connection()
    query = """
    SELECT pr.patient_id, pr.routine_id, p.name AS patient_name, r.name AS routine_name
    FROM patient_routines pr
    JOIN patients p ON pr.patient_id = p.id
    JOIN routines r ON pr.routine_id = r.id
    """
    patient_routines = pd.read_sql(query, conn)
    conn.close()
    return patient_routines

def fetch_exercise_logs(patient_id, routine_id):
    conn = get_connection()
    query = """
    SELECT date_time, duration_minutes, mood_level
    FROM exercise_logs
    WHERE patient_id = ? AND routine_id = ?
    ORDER BY date_time
    """
    exercise_logs = pd.read_sql(query, conn, params=(patient_id, routine_id))
    conn.close()
    return exercise_logs

@st.cache_data
def get_exercises_for_routine(routine_id):
    conn = get_connection()
    query = """
        SELECT e.name, e.description, e.phase, e.video
        FROM exercises e
        JOIN routine_exercises re ON e.id = re.exercise_id
        WHERE re.routine_id = ?
        ORDER BY e.phase
    """
    exercises = pd.read_sql(query, conn, params=(routine_id,))
    conn.close()
    return exercises
    
def add_user(username, password, role):
    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = get_connection()
  
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    
    conn.commit()
    conn.close()

@st.cache_data
def get_user(username):
    conn = get_connection()
    query = "SELECT username, password, role FROM users WHERE username = ?"
    df = pd.read_sql(query, conn, params=(username,))
    user = df.iloc[0] if not df.empty else None
    conn.close()
    return user

def bulk_insert_patient(df):
    conn = get_connection()
    
    # Map the columns from the CSV to match the database schema
    mapped_df = df[["NAME", "MEM_AGE", "MEM_GENDER", "MEM_RACE"]].rename(
        columns={
            "NAME": "name",
            "MEM_AGE": "age",
            "MEM_GENDER": "gender",
            "MEM_RACE": "ethnicity"
        }
    )

    # Insert DataFrame into the SQLite table
    mapped_df.to_sql("patients", conn, if_exists="append", index=False)
    
    conn.commit()
    conn.close()

def get_exercise_stats(patient_id):
    # Connect to the database
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query data
    query = """
    SELECT 
        COUNT(*) AS total_sessions,
        MAX(streak_count) AS longest_streak
    FROM (
        SELECT 
            patient_id,
            COUNT(*) AS streak_count,
            MIN(date_time) AS start_date,
            MAX(date_time) AS end_date
        FROM (
            SELECT 
                patient_id,
                date_time,
                date(date_time) - ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY date_time) AS streak_group
            FROM exercise_logs
        )
        GROUP BY patient_id, streak_group
    )
    WHERE patient_id = ?;
    """
    cursor.execute(query, (patient_id,))
    result = cursor.fetchone()
    
    total_sessions = result[0] if result else 0
    longest_streak = result[1] if result else 0
    return total_sessions, longest_streak
