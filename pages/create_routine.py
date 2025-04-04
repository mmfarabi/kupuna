import streamlit as st
import json
import os
import re
import google.generativeai as genai
import streamlit_shadcn_ui as ui

from streamlit_player import st_player
from style_helper import apply_header, card_container, apply_footer
from database import get_all_exercises, insert_routine

GEM_MODEL = 'models/gemini-1.5-flash' # os.getenv('models/gemini-1.5-flash')
GOOGLE_API_KEY = 'AIzaSyA6MLJkBbAHaBwjpBEGwwa5kL2WKWRFqRQ' # os.getenv('AIzaSyA6MLJkBbAHaBwjpBEGwwa5kL2WKWRFqRQ')

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(
    GEM_MODEL,
    generation_config={
        "temperature": 0.3,
        "top_k": 40,
        "top_p": 0.95
    }
)

def load_exercise_data():
    try:
        with open("exercise_routines.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Configuration file not found. Please contact support.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Invalid JSON format in configuration file.")
        st.stop()

exercise_data = load_exercise_data()

@st.cache_data
def generate_playlist(age, gender, ethnicity):
    PLAYLIST_PROMPT = os.getenv('PLAYLIST_PROMPT')
    request = PLAYLIST_PROMPT.format(age=age, gender=gender, ethnicity=ethnicity)
    response = model.generate_content(request)
    return response.text

@st.cache_data
def normalize_text(text):
    return re.sub(r"[\u2018\u2019\u02BB']", "", text).lower()

def find_music_links(markdown_text):
    music_titles = []
    markdown_text_normalized = normalize_text(markdown_text)

    for title, video_id in exercise_data.items():
        normalized_title = normalize_text(title)
        if normalized_title in markdown_text_normalized:
            st.write(title)
            st_player(f'https://www.youtube.com/watch?v={video_id}', key=f"music_player_{video_id}")
            music_titles.append(title)
    return ", ".join(music_titles)

def routine_select(exercise_data):
    left, right = st.columns(2)
    with left:
        mobility_level = st.selectbox(
            "Mobility level:",
            exercise_data.keys(),
            key="mobility_level_select"
        )

    with right:
        if mobility_level:
            lengths = exercise_data[mobility_level].keys()
            routine_length = st.selectbox(
                "Routine length:",
                lengths,
                key="routine_length_select"
            )

    return mobility_level, routine_length

def main():
    apply_header()
    st.title("Create Exercise Routine")

    st.markdown(
      """
      <div class="button-grid">
          <a href="member_info" target="_self" class="button-card">
            <p>Member Info</p>
            <div class="icon">&#128117;</div>
          </a>
          <a href="assign_routine" target="_self" class="button-card">
            <p>Assign Routine</p>
            <div class="icon">&#128116;</div>
          </a>
          <a href="exercise_routines" target="_self" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#129488;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")
    
    st.sidebar.header("Kūpuna Details")
    age = st.sidebar.number_input("Age", min_value=18, max_value=120, value=65, step=1, key="age_input")
    gender = st.sidebar.radio("Gender", ["Kāne (Male)", "Wahine (Female)", "Other"], key="gender_radio")
    ethnicity = st.sidebar.selectbox(
        "Race",
        ["Caucasian", "Black", "Native Hawaiian or Pacific Islander", "Filipino", 
         "Portuguese", "Japanese", "Chinese", "Other"],
        key="ethnicity_select"
    )
    if ethnicity == "Other":
        other_ethnicity = st.sidebar.text_input("Please specify ethnicity", key="other_ethnicity")
        if other_ethnicity:
            ethnicity = other_ethnicity
    
    st.sidebar.markdown("### Kūpuna Summary")
    st.sidebar.markdown(f"**Age**: {age}")
    st.sidebar.markdown(f"**Gender**: {gender}")
    st.sidebar.markdown(f"**Race**: {ethnicity}")

    mobility_level, routine_length = card_container(
        "routine_selection",
        routine_select,
        exercise_data
    )
    
    selected_exercises = {}

    if mobility_level and routine_length:
        st.header(f"Exercise Routine for {mobility_level} Mobility Level ({routine_length})")
        routine = exercise_data[mobility_level][routine_length]
    
        for phase, exercises in routine.items():
            st.subheader(phase)
    
            options = exercises
            
            selected_exercise = st.radio(
                label=f"Select an exercise for {phase}:",
                options=options,
                format_func=lambda x: x['name'] if x else "None",
                key=f"exercise_select_{mobility_level}_{routine_length}_{phase}"
            )
    
            selected_exercises[phase] = selected_exercise
    
            columns = st.columns(len(exercises))
    
            for col, exercise in zip(columns, exercises):
                with col:
                    st.markdown(f"**{exercise['name']}**")
                    if (len(exercises) > 1):
                        st_player(
                            exercise['video'], 
                            key=f"exercise_player_{exercise['id']}_{phase}_col{columns.index(col)}"
                        )
                    else:
                        _,center,_ = st.columns([1,2,1])
                        with center:
                            st_player(
                                exercise['video'], 
                                key=f"exercise_player_{exercise['id']}_{phase}_center"
                            )
                        
        if st.button("Create Routine", key="create_routine_btn"):
            st.subheader("Generated Routine")
            all_sections_selected = all(value is not None for value in selected_exercises.values())
            if not all_sections_selected:
                st.error("Please select one exercise from each section before generating the routine.")
            else:
                col1, col2 = st.columns(2)
        
                with col1:
                    st.markdown("### 🩰 Exercises")
                    for section, exercise in selected_exercises.items():
                        st.markdown(f"**{section} - {exercise['name']}**")
                        st.markdown(f"*{exercise['description']}*")
                        st.video(
                            exercise['video'], 
                            format='video/mp4', 
                            start_time=0,
                            key=f"final_video_{exercise['id']}"
                        )
        
                with col2:
                    st.markdown("### 🎵 Therapeutic Music")
                    st.markdown("#### 👤 Kūpuna Details")
                    st.markdown(f"- **Age**: {age}")
                    st.markdown(f"- **Gender**: {gender}")
                    st.markdown(f"- **Race**: {ethnicity}")
                    st.divider()

                    st.markdown("#### 🎶 Music Titles")
                    playlist = generate_playlist(age, gender, ethnicity)
                    st.markdown(playlist)
                    st.divider()

                    st.markdown("#### 📺 Music Videos")
                    music_titles = find_music_links(playlist)
                    st.session_state["music_titles"] = music_titles
        
        with st.form(key="routine_form"):
            st.subheader("Routine Details")
            routine_name = st.text_input("Routine Name", "", key="routine_name")
            routine_description = st.text_area("Routine Description (Optional)", "", key="routine_desc")
            music_field = st.text_input("Suggested Music", st.session_state.get("music_titles", ""), key="music_input")

            exercise_ids_string = ", ".join([str(exercise["id"]) for exercise in selected_exercises.values()])
            st.text_input("Selected Exercise IDs", value=exercise_ids_string, disabled=True, key="exercise_ids_display")

            submit_button = st.form_submit_button(label="Save Routine", key="save_routine_btn")
            
            if submit_button:
                if routine_name == "":
                    st.error("Routine name is required!")
                else:                    
                    exercise_ids = [int(exercise["id"]) for exercise in selected_exercises.values()]
                    insert_routine(routine_name, routine_description, music_field, exercise_ids)
                    st.success(f'Routine {routine_name} has been created. Please click "Assign Routine" button to assign routine to a kūpuna.')

        apply_footer()

if __name__ == "__main__":
    main()
