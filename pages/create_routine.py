import streamlit as st

from style_helper import apply_header

from database import get_all_exercises, insert_routine

def main():
    apply_header()
    st.title("Create Exercise Routine")

    st.markdown(
      """
      <div class="button-grid">
          <a href="assign_routine" class="button-card">
            <p>Assign Routine</p>
            <div class="icon">&#128116;</div>
          </a>
          <a href="exercise_routines" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#128221;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    # Load exercise routines
    exercise_data = get_all_exercises()

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")
    
    # Input fields for dementia subject's details
    st.sidebar.header("Subject Details")
    age = st.sidebar.number_input("Age", min_value=18, max_value=120, value=65, step=1)
    gender = st.sidebar.radio("Gender", ["Male", "Female", "Other"])
    ethnicity = st.sidebar.selectbox(
        "Ethnicity",
        ["Caucasian", "Native Hawaiian or Pacific Islander", "Filipino", "Portuguese", "Japanese", "Chinese", "Other"]
    )
    if ethnicity == "Other":
        other_ethnicity = st.sidebar.text_input("Please specify ethnicity")
        if other_ethnicity:
            ethnicity = other_ethnicity
    
    # Display the selected details in the sidebar for review
    st.sidebar.markdown("### Subject Details Summary")
    st.sidebar.markdown(f"**Age**: {age}")
    st.sidebar.markdown(f"**Gender**: {gender}")
    st.sidebar.markdown(f"**Ethnicity**: {ethnicity}")

    # Mobility level selection
    mobility_level, routine_length = card_container(
        "routine_selection",
        routine_select,
        exercise_data
    )
    
    # Dictionary to store selected exercises
    selected_exercises = {}

if __name__ == "__main__":
    main()
