import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit_shadcn_ui as ui

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
            <div class="icon">&#129488;</div>
          </a>
          <a href="dementia_info" target="_self" class="button-card">
            <p>Dementia Info</p>
            <div class="icon">&#128106;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")

    # Fetch available routines and patients
    patients_df = fetch_patients()
    routines_df = fetch_routines()
    patient_routines_df = fetch_patient_routines()
    
    # Display patient and routine data in the main area
    st.header('Kūpunas Assigned to Routines')
    ui.table(data=patient_routines_df)

    # Move the patient-routine selection to the sidebar
    selected_patient_routine = st.sidebar.selectbox(
        'Select a kūpuna and assigned routine',
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
        st.header(f'Exercise log for {selected_patient_name} and routine {selected_routine_name}')
        ui.table(data=exercise_logs_df)
        
        if not exercise_logs_df.empty:
            exercise_logs_df['date_time'] = pd.to_datetime(exercise_logs_df['date_time'])
            plt.figure(figsize=(10, 6))
            sns.lineplot(x='date_time', y='mood_level', data=exercise_logs_df, marker='o', color='#FF3583')
            plt.title(f'Mood Level Over Time for {selected_patient_name} - {selected_routine_name}')
            plt.xlabel('Date')
            plt.ylabel('Mood Level')
            plt.xticks(rotation=45)
            st.pyplot(plt)

            # Get the most recent date in the logs
            max_logged_date = exercise_logs_df['date_time'].max().date()
        else:
            st.warning("No exercise log data available for the selected kūpuna and routine.")
            max_logged_date = None

        st.sidebar.header('Log a New Exercise')
        date_input = st.sidebar.date_input('Date')
        duration_input = st.sidebar.number_input('Duration (minutes)', min_value=15)
        mood_level_input = st.sidebar.selectbox('Mood Level', [1, 2, 3, 4, 5])
        comments_input = st.sidebar.text_area('Comments (optional)', '')

        # Button to save the new exercise log entry
        if st.sidebar.button('Enter Exercise Log'):
            if max_logged_date and date_input <= max_logged_date:
                ui.alert_dialog(show=True, 
                                title="Invalid Date", 
                                description=f"Date must be greater than the most recent exercise date: {max_logged_date}", 
                                confirm_label="OK", 
                                cancel_label="Cancel",
                                key="routine_created_dialog")
            else:
                try:
                    insert_exercise_log(selected_patient_id, selected_routine_id, date_input, duration_input, mood_level_input, comments_input)
                    st.sidebar.success('Exercise log saved successfully!')
                    st.rerun()
                except sqlite3.IntegrityError:
                    ui.alert_dialog(show=True, 
                                title="Invalid Date", 
                                description="Please change the date, an exercise entry with the same exact date and time already exists.", 
                                confirm_label="OK", 
                                cancel_label="Cancel",
                                key="routine_created_dialog")
    else:
        st.warning("Please select a kūpuna and routine combination to track mood levels and log data.")        

if __name__ == "__main__":
    main()
