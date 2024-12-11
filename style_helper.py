import streamlit as st
import os

from streamlit_extras.stylable_container import stylable_container

def apply_header():
  st.set_page_config(layout="wide", page_title="Kūpuna Care", page_icon="👵")

  STYLE_CSS = os.getenv('STYLE_CSS')
  st.markdown(STYLE_CSS, unsafe_allow_html=True)
  
  html_content = """<div class="e2_21">
      <div class="header-text-container">
          <div class="e1_15">KŪPUNA CARE</div>
          <div class="e2_23"></div>
          <div class="e2_22">Lōkahi Innovation</div>
      </div>
      <div class="header-image">
          <img src="https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/hawaii.png" alt="Header Image">
      </div>
  </div>"""
  st.markdown(html_content, unsafe_allow_html=True)
