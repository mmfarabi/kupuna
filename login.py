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

        st.write(user)
        st.write(user.shape)
        st.write(user["password"])
          
        if user is not None:
            if bcrypt.checkpw(password.encode(), user["password"].item()):
                st.session_state["role"] = user[2]
                st.success(f"Logged in as {user[2]}")
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
        add_user(username, hashed_pw, role)
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
