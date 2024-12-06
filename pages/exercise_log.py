import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from database import fetch_routines, fetch_patients, fetch_patient_routines, fetch_exercise_logs, insert_exercise_log
from style_helper import apply_header

def main():
    apply_header()

    st.title("Exercise Log")

    st.markdown(
      """
      <div class="button-grid">
          <a href="exercise_routines" target="_self" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#128221;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")

if __name__ == "__main__":
    main()
