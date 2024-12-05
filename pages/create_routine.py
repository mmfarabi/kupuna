import streamlit as st

from style_helper import apply_header, card_container

from database import get_all_exercises, insert_routine

# Dictionary of songs and their corresponding YouTube links
youtube_links = json.loads(os.getenv('YOUTUBE_LINKS'))

@st.cache_data
def generate_playlist(age, gender, ethnicity):
    PLAYLIST_PROMPT = os.getenv('PLAYLIST_PROMPT')
    request = PLAYLIST_PROMPT.format(age=age, gender=gender, ethnicity=ethnicity)
    response = model.generate_content(request)
    return response.text

@st.cache_data
def normalize_text(text):
    # Remove special characters and normalize spaces
    return re.sub(r"[\u2018\u2019\u02BB']", "", text).lower()

def find_music_links(markdown_text):
    music_links = []
    
    # Normalize markdown text for case-insensitive matching
    markdown_text_normalized = normalize_text(markdown_text)

    # Search for song titles in the markdown text
    for title, video_id in youtube_links.items():
        normalized_title = normalize_text(title)
        if normalized_title in markdown_text_normalized:
            # Print only if a match is found
            st.write(title)
            st_player(f'https://www.youtube.com/watch?v={video_id}')
            music_links.append(video_id)

    return music_links

def routine_select(exercise_data):
    left, right = st.columns(2)
    # Mobility level selection
    with left:
        mobility_level = st.selectbox(
            "Mobility level:",
            exercise_data.keys()
        )

    with right:
    # Length of routine selection
        if mobility_level:
            lengths = exercise_data[mobility_level].keys()
            routine_length = st.selectbox(
                "Routine length:",
                lengths
            )

    return mobility_level, routine_length

def main():
    apply_header()
    st.title("Create Exercise Routine")

    st.markdown(
      """
      <div class="button-grid">
          <a href="assign_routine" class="button-card">
            <p>Assign Routine</p>
            <div class="icon">&#128116;</div>
          </a>
          <a href="exercise_routines" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#128221;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    # Load exercise routines
    exercise_data = get_all_exercises()

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")
    
    # Input fields for dementia subject's details
    st.sidebar.header("Subject Details")
    age = st.sidebar.number_input("Age", min_value=18, max_value=120, value=65, step=1)
    gender = st.sidebar.radio("Gender", ["Male", "Female", "Other"])
    ethnicity = st.sidebar.selectbox(
        "Ethnicity",
        ["Caucasian", "Native Hawaiian or Pacific Islander", "Filipino", "Portuguese", "Japanese", "Chinese", "Other"]
    )
    if ethnicity == "Other":
        other_ethnicity = st.sidebar.text_input("Please specify ethnicity")
        if other_ethnicity:
            ethnicity = other_ethnicity
    
    # Display the selected details in the sidebar for review
    st.sidebar.markdown("### Subject Details Summary")
    st.sidebar.markdown(f"**Age**: {age}")
    st.sidebar.markdown(f"**Gender**: {gender}")
    st.sidebar.markdown(f"**Ethnicity**: {ethnicity}")

    # Mobility level selection
    mobility_level, routine_length = card_container(
        "routine_selection",
        routine_select,
        exercise_data
    )
    
    # Dictionary to store selected exercises
    selected_exercises = {}

    # Display routine based on selection
    if mobility_level and routine_length:
        st.header(f"Exercise Routine for {mobility_level} Mobility Level ({routine_length})")
        routine = exercise_data[mobility_level][routine_length]
    
        # Loop through each section and allow caregivers to select an exercise
        for phase, exercises in routine.items():
            st.subheader(phase)  # Display the phase name (e.g., "Warm-Up")
    
            # Exercise options for the current phase
            options = exercises
            
            # Create a radio button for the phase
            selected_exercise = st.radio(
                label=f"Select an exercise for {phase}:",
                options=options,
                format_func=lambda x: x['name'] if x else "None",  # Show "None" if unselected
                key=f"{mobility_level}-{routine_length}-{phase}"
            )
    
            # Store the selected exercise
            selected_exercises[phase] = selected_exercise
    
            # Create columns equal to the number of exercises
            columns = st.columns(len(exercises))
    
            for col, exercise in zip(columns, exercises):
                with col:
                    # Display the exercise name
                    st.markdown(f"**{exercise['name']}**")
                    
                    # Display the video
                    st.video(exercise['video'])
    
        # Button to generate exercise routine
        if st.button("Create Routine"):
            st.subheader("Generated Routine")
            all_sections_selected = all(value is not None for value in selected_exercises.values())
            if not all_sections_selected:
                st.error("Please select one exercise from each section before generating the routine.")
            else:
                
                # Create columns for exercises and music
                col1, col2 = st.columns(2)
        
                with col1:
                    st.markdown("### 🩰 Exercises")
                    for section, exercise in selected_exercises.items():
                        st.markdown(f"**{section} - {exercise['name']}**")
                        st.markdown(f"*{exercise['description']}*")
                        st_player(exercise['video'])
        
                with col2:
                    st.markdown("### 🎵 Therapeutic Music")
    
                    # Subject Demographics Section
                    st.markdown("#### 👤 Subject Details")
                    st.markdown(f"- **Age**: {age}")
                    st.markdown(f"- **Gender**: {gender}")
                    st.markdown(f"- **Ethnicity**: {ethnicity}")
                    st.divider()  # Adds a horizontal divider for better structure

                    st.markdown("#### 🎶 Music Titles")
                    playlist = generate_playlist(age, gender, ethnicity)
                    st.markdown(playlist)
                    st.divider()

                    st.markdown("#### 📺 YouTube Videos")
                    music_links = find_music_links(playlist)
    
        # Form below the routine generation button
        with st.form(key="routine_form"):
            st.subheader("Routine Details")
        
            # Routine name input field (required)
            routine_name = st.text_input("Routine Name", "")

            # Description field (optional)
            routine_description = st.text_area("Routine Description (Optional)", "")
            
            # Optional music field (optional)
            music_field = st.text_input("Optional Music", "")
        
            # Read-only field for selected exercise IDs
            exercise_ids_string = ", ".join([str(exercise["id"]) for exercise in selected_exercises.values()])
            st.text_input("Selected Exercise IDs", value=exercise_ids_string, disabled=True)

            # Checkbox to create a YouTube playlist
            create_playlist = st.checkbox("Create Playlist")

            # Submit button for the form
            submit_button = st.form_submit_button(label="Save Routine")
            
        if submit_button:
            if routine_name == "":
                st.error("Routine name is required!")
            else:
                exercise_ids = [int(exercise["id"]) for exercise in selected_exercises.values()]
                insert_routine(routine_name, music_field, [1])
                st.success(f"Routine {routine_name} has been created!")
                st.balloons()

                if create_playlist:
                    playlist = create_playlist(routine_name, routine_description)
                    for music_title, video_id in playlist:
                        add_to_playlist(playlist, video_id)


if __name__ == "__main__":
    main()
