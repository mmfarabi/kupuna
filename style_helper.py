import streamlit as st
import os

from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.bottom_container import bottom

STYLE_CSS = os.getenv('STYLE_CSS')

def apply_header():
  st.set_page_config(layout="wide", page_title="Kūpuna Care", page_icon="👵")  
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

def apply_footer():  
  st.markdown(STYLE_CSS, unsafe_allow_html=True)
  
  html_content = """<div class="footer">
    <p>© 2024 Kūpuna Care.</p>
  </div>"""

  with bottom():
    st.markdown(html_content, unsafe_allow_html=True)

def card_container(key, content_func, *args, **kwargs):
    # Create a container to group components
    with stylable_container(
        key=key,
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.2), -3px -3px 8px rgba(255, 255, 255, 0.8);
            }
            """
    ):
      result = content_func(*args, **kwargs) if callable(content_func) else None
      return result
