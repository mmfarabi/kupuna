import streamlit as st
import sqlite3
import bcrypt

from database import initialize_database, get_user, add_user

initialize_database()

# Session State for login
if "role" not in st.session_state:
    st.session_state["role"] = None

def login_page(col):
    with col:
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      if st.button("Login"):
        user = get_user(username)
          
        if user is not None:
            if bcrypt.checkpw(password.encode(), user["password"]):
                role = user.iloc(2)
                st.session_state["role"] = role
                st.success(f"Welcome {user[0]}. You are logged in as {role}")
                if role == "coach":
                    st.switch_page("pages/create_routine.py")
                elif role == "caregiver":
                    st.switch_page("pages/exercise_log.py")
            else:
                st.error("Invalid login.")
        else:
            st.error("Invalid login.")

def register_page(col):
    with col:
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      role = st.selectbox("Role", ["coach", "caregiver"])
      if st.button("Register"):
        add_user(username, password, role)
        st.success("User registered successfully!")
      
def main():
    _, center, _ = st.columns([1,2,1])
    st.sidebar.title("Actions")
    option = st.sidebar.radio("Choose Action", ["Login", "Register"])
    if option == "Login":
        login_page(center)
    else:
        register_page(center)

if __name__ == "__main__":
    main()
