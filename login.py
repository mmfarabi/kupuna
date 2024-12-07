import streamlit as st
import sqlite3
import bcrypt

from style_helper import apply_header
from database import initialize_database, get_user, add_user

def login_page(col):
    with col:
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      if st.button("Login"):
        user = get_user(username)
          
        if user is not None:
            if bcrypt.checkpw(password.encode(), user["password"]):
                role = user[2]
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
    apply_header()

    initialize_database()

    # Session State for login
    if "role" not in st.session_state:
        st.session_state["role"] = None
    
    _, center, _ = st.columns([1,2,1])
    center.title("Mock Login")

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")
    st.sidebar.title("Actions")
    option = st.sidebar.radio("Choose Action", ["Login", "Register"])
    if option == "Login":
        login_page(center)
    else:
        register_page(center)

    with center:
        with st.expander("Test Users"):
            st.code("Username: don\nPassword: password\nRole: coach")        
            st.code("Username: deb\nPassword: password\nRole: caregiver")

        members = """
        PRIMARY_PERSON_KEY,MEMBER_ID,MEM_GENDER,MEM_RACE,MEM_ETHNICITY,MEM_ZIP3,MEM_MSA_NAME,MEM_STATE
        1E9F89247B2EA224292BDA829,1E9F89247B2EA224292BDA829,M,,,967,"NON-MSA AREA, HI",HI
        F760929731123ECC986CE311B,F760929731123ECC986CE311B,F,,,968,"URBAN HONOLULU, HI",HI
        B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,M,,,968,"URBAN HONOLULU, HI",HI
        222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,968,"URBAN HONOLULU, HI",HI
        111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,F,,,968,"URBAN HONOLULU, HI",HI
        1E9F89247B2EA224292BDA829,1E9F89247B2EA224292BDA829,M,,,967,"NON-MSA AREA, HI",HI
        F760929731123ECC986CE311B,F760929731123ECC986CE311B,F,,,487,"NON-MSA AREA, MI",MI
        B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,M,,,483,"WARREN-TROY-FARMINGTON HILLS, MI",MI
        222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,484,"FLINT, MI",MI
        111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,F,,,485,"FLINT, MI",MI
        """
        st.text_area("Members", value=members.strip(), height=300)

        enrollment = """
        PRIMARY_PERSON_KEY,MEMBER_ID,MEMBER_MONTH_START_DATE,YEARMO,MEM_AGE,RELATION,MEM_MSA_NAME,PAYER_LOB,PAYER_TYPE,PROD_TYPE,QTY_MM_MD,QTY_MM_RX,QTY_MM_DN,QTY_MM_VS,MEM_STAT,PRIMARY_CHRONIC_CONDITION_ROLLUP_ID,PRIMARY_CHRONIC_CONDITION_ROLLUP_DESC
        7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,2023-07-01,202307,76,SUBSCRIBER,"WARREN-TROY-FARMINGTON HILLS, MI",MEDICARE,MP,DENTAL,0.0,0.0,1.0,0.0,,102.0,102 - SEVERE DEMENTIA
        111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,2023-05-01,202305,75,SUBSCRIBER,"FLINT, MI",MEDICARE SUPPLEMENT,MS,VISION,0.0,0.0,0.0,1.0,,102.0,102 - SEVERE DEMENTIA
        222C720211EE79B712933E434,222C720211EE79B712933E434,2023-07-01,202307,83,SUBSCRIBER,"FLINT, MI",MEDICARE,MP,VISION,0.0,0.0,0.0,1.0,,102.0,102 - SEVERE DEMENTIA
        B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,2023-09-01,202309,80,SUBSCRIBER,"WARREN-TROY-FARMINGTON HILLS, MI",MEDICARE,MP,RX,0.0,1.0,0.0,0.0,,102.0,102 - SEVERE DEMENTIA
        F760929731123ECC986CE311B,F760929731123ECC986CE311B,2022-10-01,202210,85,SUBSCRIBER,"NON-MSA AREA, MI",MEDICARE SUPPLEMENT,MS,MEDICAL,1.0,0.0,0.0,0.0,,102.0,102 - SEVERE DEMENTIA
        """
        st.text_area("Enrollment", value=enrollment.strip(), height=300)

if __name__ == "__main__":
    main()
