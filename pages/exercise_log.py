import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from database import fetch_routines, fetch_patients, fetch_patient_routines, fetch_exercise_logs, insert_exercise_log
from style_helper import apply_header

def main():
    apply_header()

    st.title("Exercise Log")

    st.markdown(
      """
      <div class="button-grid">
          <a href="exercise_routines" target="_self" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#128221;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")

    # Fetch available routines and patients
    patients_df = fetch_patients()
    routines_df = fetch_routines()
    patient_routines_df = fetch_patient_routines()
    
    # Display patient and routine data in the main area
    st.header('Kūpunas and Routines')
    st.dataframe(patient_routines_df)

    # Move the patient-routine selection to the sidebar
    selected_patient_routine = st.sidebar.selectbox(
        'Select a kūpuna and routine combination',
        patient_routines_df['patient_name'] + ' - ' + patient_routines_df['routine_name'],
        index=None  # Set default to no selection
    )

    # Check if a selection has been made
    if selected_patient_routine:
        # Extract selected patient and routine IDs
        selected_patient_name, selected_routine_name = selected_patient_routine.split(' - ')
        selected_patient_id = patient_routines_df.loc[patient_routines_df['patient_name'] == selected_patient_name, 'patient_id'].values[0]
        selected_routine_id = patient_routines_df.loc[patient_routines_df['routine_name'] == selected_routine_name, 'routine_id'].values[0]
    
        # Plot the mood levels over time for the selected patient and routine
        st.header('Mood Level Over Time')
        exercise_logs_df = fetch_exercise_logs(selected_patient_id, selected_routine_id)
        if not exercise_logs_df.empty:
            exercise_logs_df['date_time'] = pd.to_datetime(exercise_logs_df['date_time'])
            plt.figure(figsize=(10, 6))
            sns.lineplot(x='date_time', y='mood_level', data=exercise_logs_df, marker='o')
            plt.title(f'Mood Level Over Time for {selected_patient_name} - {selected_routine_name}')
            plt.xlabel('Date')
            plt.ylabel('Mood Level')
            plt.xticks(rotation=45)
            st.pyplot(plt)
        else:
            st.warning("No exercise log data available for the selected kūpuna and routine.")

        st.sidebar.header('Log a New Exercise')
        date_input = st.sidebar.date_input('Date')
        duration_input = st.sidebar.number_input('Duration (minutes)', min_value=15)
        mood_level_input = st.sidebar.selectbox('Mood Level', [1, 2, 3, 4, 5])
        comments_input = st.sidebar.text_area('Comments (optional)', '')



if __name__ == "__main__":
    main()
