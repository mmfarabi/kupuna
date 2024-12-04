import streamlit as st

def initialize_session_state():
    # Initialize session state variables if they don't exist
    st.session_state.setdefault("username", None)
    st.session_state.setdefault("role", None)
    st.session_state.setdefault("is_logged_in", False)
