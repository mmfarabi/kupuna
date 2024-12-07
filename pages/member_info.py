import streamlit as st

from style_helper import apply_header

def main():    
    apply_header()
    st.title("Member Info")

    st.markdown(
      """
      <div class="button-grid">
          <a href="create_routine" target="_self" class="button-card">
            <p>Create Routine</p>
            <div class="icon">&#x1F57A;</div>
          </a>
          <a href="assign_routine" target="_self" class="button-card">
            <p>Assign Routine</p>
            <div class="icon">&#128116;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
