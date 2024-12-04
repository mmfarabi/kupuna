import streamlit as st

from utils import check_access

def main():
    # Check access
    check_access("coach")

    st.title("Create Exercise Routine")
    st.write("This is a placeholder for the Create Exercise Routine page.")

if __name__ == "__main__":
    main()
