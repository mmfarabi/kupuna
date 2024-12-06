import streamlit as st

from style_helper import apply_header, card_container
from database import fetch_patients, fetch_routines, assign_patient_to_routine

def main():    
    apply_header()
    st.title("Assign Routine")

    st.markdown(
      """
      <div class="button-grid">
          <a href="create_routine" target="_self" class="button-card">
            <p>Create Routine</p>
            <div class="icon">&#128116;</div>
          </a>
          <a href="exercise_routines" target="_self" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#128221;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")
    
    left, right = st.columns(2)
    # Display patients
    with left:
        st.header('Patients')
        patients_df = fetch_patients()
        st.dataframe(patients_df)
        
    # Display routines
    with right:
        st.header('Routines')
        routines_df = fetch_routines()
        st.dataframe(routines_df)

    # Proceed if both patients and routines are available
    if not patients_df.empty and not routines_df.empty:
        # Create dictionaries for patients and routines mapping IDs to names
        patients_dict = {row['id']: row['name'] for _, row in patients_df.iterrows()}
        routines_dict = {row['id']: row['name'] for _, row in routines_df.iterrows()}
   
        # Move widgets to sidebar
        st.sidebar.header('Assign a Routine to a Patient')
       
        # Use names in selectbox and pass IDs to the assign function
        selected_patient_name = st.sidebar.selectbox('Select a patient', options=list(patients_dict.values()))
        selected_routine_name = st.sidebar.selectbox('Select a routine', options=list(routines_dict.values()))
   
        # Get the corresponding IDs for the selected patient and routine
        selected_patient_id = [id for id, name in patients_dict.items() if name == selected_patient_name]
        selected_routine_id = [id for id, name in routines_dict.items() if name == selected_routine_name]
   
        # Ensure that we have found valid IDs
        if selected_patient_id and selected_routine_id:
            selected_patient_id = selected_patient_id[0]
            selected_routine_id = selected_routine_id[0]
   
            # Button to assign the routine to the patient (in the sidebar)
            if st.sidebar.button('Assign Routine'):
                assign_patient_to_routine(selected_patient_id, selected_routine_id)
                st.sidebar.success(f"Routine '{selected_routine_name}' assigned to patient '{selected_patient_name}'.")
                st.balloons()
        else:
            st.sidebar.warning("Please select a valid patient and routine.")
    else:
        st.warning("Unable to assign routine as patient or routine data is missing.")

if __name__ == "__main__":
    main()
