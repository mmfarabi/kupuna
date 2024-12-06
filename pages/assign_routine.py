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

if __name__ == "__main__":
    main()
