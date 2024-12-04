import streamlit as st

def check_access(role):
  if st.session_state.get("role") != role:
    st.error("You do not have permission to view this page.")
    st.switch_page("login.py")  # Redirect to login page

def check_login():
  if not st.session_state.get("role"):
    st.error("You must be logged in to view this page.")
    st.switch_page("login.py")  # Redirect to the login page
