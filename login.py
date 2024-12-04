import streamlit as st
import sqlite3
import bcrypt

# Session State for login
if "role" not in st.session_state:
    st.session_state["role"] = None

def login_page(col):
    with col:
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      if st.button("Login"):
          pass

def register_page(col):
    with col:
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      role = st.selectbox("Role", ["coach", "caregiver"])
      if st.button("Register"):
          pass
      
def main():
    _, center_col, _ = st.columns([1,2,1]) 
    st.sidebar.title("Actions")
    option = st.sidebar.radio("Choose Action", ["Login", "Register"])
    if option == "Login":
        login_page(center)
    else:
        register_page(center)

if __name__ == "__main__":
    main()
