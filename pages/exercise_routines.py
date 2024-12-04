import streamlit as st

from utils import check_access

def main():
    # Check access
    check_access("caregiver")

    st.title("Exercise Log")
    st.write("This is a placeholder for the Exercise Log page.")

if __name__ == "__main__":
    main()
