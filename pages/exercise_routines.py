import streamlit as st

from database import fetch_routines, get_exercises_for_routine

def main():    
    st.title("Exercise Routines")

    st.markdown(
      """
      <div class="button-grid">
          <a href="#" class="button-card">
            <p>Create Routine</p>
            <div class="icon">&#x1F57A;</div>
          </a>
          <div class="button-card">
            <p>Assign Routine</p>
            <div class="icon">&#128116;</div>
          </div>
          <div class="button-card">
            <p>Exercise Log</p>
            <div class="icon">&#128221;</div>
          </div>
      </div>
      """, unsafe_allow_html=True)

    
    # Fetch all routines
    routines = fetch_routines()

    # Display routine selection
    if not routines.empty:
        routine_id = st.selectbox(
            "Select a Routine",
            options=routines["id"],
            format_func=lambda rid: routines.loc[routines["id"] == rid, "name"].values[0]
        )
        
        # Fetch and display routine details and exercises
        if routine_id:
            routine_details = routines.loc[routines["id"] == routine_id].iloc[0]
            st.subheader(f"Routine: {routine_details['name']}")
            
            # Display routine music if available
            if routine_details["music"]:
                st.markdown(f"**Music:** {routine_details['music']}")
            
            # Fetch and display exercises for the selected routine
            exercises = get_exercises_for_routine(routine_id)
            st.subheader("Exercises")
            if not exercises.empty:
                for _, exercise in exercises.iterrows():
                    st.markdown(f"### {exercise['name']} ({exercise['phase']})")
                    st.write(exercise["description"])
                    if exercise["video"]:
                        st.video(f"https://www.youtube.com/watch?v={exercise['video']}")
            else:
                st.write("No exercises found for this routine.")
    else:
        st.write("No routines available.")

if __name__ == "__main__":
    main()
