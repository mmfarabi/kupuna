import streamlit as st

def check_access(role):
  if st.session_state.get("role") != role:
    st.error("You do not have permission to view this page.")
    st.switch_page("login.py")  # Redirect to login page
