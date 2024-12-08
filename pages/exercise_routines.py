import streamlit as st
import streamlit_shadcn_ui as ui

from database import fetch_routines, get_exercises_for_routine
from style_helper import apply_header

def main():    
    apply_header()

    st.title("Exercise Routines")

    role = st.session_state.get("role", None)

    # Conditional display of buttons based on role
    if role == "coach":
        st.markdown(
            """
            <div class="button-grid">
                <a href="create_routine" target="_self" class="button-card">
                    <p>Create Routine</p>
                    <div class="icon">&#x1F57A;</div>
                </a>
                <a href="assign_routine" target="_self" class="button-card">
                    <p>Assign Routine</p>
                    <div class="icon">&#128116;</div>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif role == "caregiver":
        st.markdown(
            """
            <div class="button-grid">
                <a href="exercise_log" target="_self" class="button-card">
                    <p>Exercise Log</p>
                    <div class="icon">&#128200;</div>
                </a>
                <a href="dementia_info" target="_self" class="button-card">
                    <p>Dementia Info</p>
                    <div class="icon">&#128106;</div>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
          """
          <div class="button-grid">
              <a href="create_routine" target="_self" class="button-card">
                <p>Create Routine</p>
                <div class="icon">&#x1F57A;</div>
              </a>
              <a href="assign_routine" target="_self" class="button-card">
                <p>Assign Routine</p>
                <div class="icon">&#128116;</div>
              </a>
              <a href="exercise_log" target="_self" class="button-card">
                <p>Exercise Log</p>
                <div class="icon">&#128200;</div>
              </a>
          </div>
          """, unsafe_allow_html=True)

    # Fetch all routines
    routines = fetch_routines()

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")
    
    # Display routine selection
    if not routines.empty:
        routine_id = st.sidebar.selectbox(
            "Select a Routine",
            options=routines["id"],
            format_func=lambda rid: routines.loc[routines["id"] == rid, "name"].values[0]
        )
        
        # Fetch and display routine details and exercises
        if routine_id:
            routine_details = routines.loc[routines["id"] == routine_id].iloc[0]
            st.subheader(f"Routine: {routine_details['name']}")

            # Display routine description if available
            if routine_details["description"]:
                st.markdown(f"**Description:** {routine_details['description']}")
            
            # Display routine music if available
            if routine_details["music"]:
                st.markdown(f"**Music:** {routine_details['music']}")
            
            # Fetch and display exercises for the selected routine
            exercises = get_exercises_for_routine(routine_id)
            
            st.subheader("Exercises")
            if not exercises.empty:
                ui.table(data=exercises)
                
                for _, exercise in exercises.iterrows():
                    st.markdown(f"### {exercise['name']} ({exercise['phase']})")
                    st.write(exercise["description"])
                    if exercise["video"]:
                        _,center,_ = st.columns([1,2,1])
                        with center:
                            st.video(exercise['video'])
            else:
                st.write("No exercises found for this routine.")
    else:
        st.write("No routines available.")

if __name__ == "__main__":
    main()
