import streamlit as st
import pandas as pd
import random
import io
import streamlit_shadcn_ui as ui

from style_helper import apply_header, apply_footer
from database import fetch_patients, bulk_insert_patient

# Define race categories and ethnicity mapping
race_categories = [
    "Caucasian", "Black", "Native Hawaiian or Pacific Islander", "Portuguese",
    "Filipino", "Japanese", "Chinese"
]

ethnicity_mapping = {
    "Caucasian": 2,  # Not Hispanic
    "Black": 3,
    "Native Hawaiian or Pacific Islander": 3,  # Unknown
    "Portuguese": 2,  # Not Hispanic
    "Filipino": 1,  # Hispanic
    "Japanese": 3,  # Unknown
    "Chinese": 3    # Unknown
}

# Fill missing MEM_RACE and set MEM_ETHNICITY
def assign_race_ethnicity(row):
    race = random.choice(race_categories)
    ethnicity = ethnicity_mapping[race]
    return pd.Series([race, ethnicity])

# Set NAME based on MEM_GENDER, MEM_RACE, MEM_ETHNICITY
def assign_name(row):
    # Gender-specific names for each race and ethnicity
    race_to_name = {
        "Caucasian": {
            "M": [
                "Alexander Baldwin", "Henry Perrine", "Ethan Taylor", 
                "William Scott", "James Hunter"
            ] if row["MEM_ETHNICITY"] == 2 else [
                "Juan Garcia", "Carlos Diaz", "Miguel Torres", 
                "Luis Ramirez", "Pedro Sanchez"
            ],
            "F": [
                "Emily Cooke", "Olivia Brown", "Sophia Harris", 
                "Emma Thompson", "Charlotte Evans"
            ] if row["MEM_ETHNICITY"] == 2 else [
                "Maria Gonzalez", "Isabella Martinez", "Ana Lopez", 
                "Lucia Morales", "Elena Navarro"
            ]
        },
        "Native Hawaiian or Pacific Islander": {
            "M": [
                "Mike Malu", "Noah Kaipo", "Lani Kealoha", 
                "Kimo Hekili", "Koa Malakai"
            ],
            "F": [
                "Leilani Aloha", "Moana Kea", "Jennifer Lani", 
                "Hina Kaleo", "Debbie Makana"
            ]
        },
        "Portuguese": {
            "M": [
                "Antonio Silva", "Manuel Sousa", "Joao Mendes", 
                "Carlos Almeida", "Francisco Moreira"
            ],
            "F": [
                "Sofia Costa", "Isabel Ferreira", "Ana Oliveira", 
                "Catarina Rocha", "Teresa Pires"
            ]
        },
        "Filipino": {
            "M": [
                "Jose Rizal", "Andres Bonifacio", "Manuel Quezon", 
                "Ramon Magsaysay", "Lapu-Lapu"
            ],
            "F": [
                "Maria Clara", "Gabriela Silang", "Corazon Aquino", 
                "Imelda Santos", "Jocelyn Cruz"
            ]
        },
        "Japanese": {
            "M": [
                "Greg Tanaka", "Hiroshi Yamamoto", "Steve Suzuki", 
                "Kenji Takeda", "Kevin Kobayashi"
            ],
            "F": [
                "Mary Sato", "Akiko Nakamura", "Eunice Takahashi", 
                "Hana Matsumoto", "Yuki Fujimoto"
            ]
        },
        "Chinese": {
            "M": [
                "David Zhang", "Li Wei", "John Wang", 
                "Kevin Chen", "Tony Huang"
            ],
            "F": [
                "Lillian Mei", "Xiao Hong", "Julia Yi", 
                "Angela Lin", "Grace Liu"
            ]
        },
        "Black": {
            "M": [
                "James Brown", "Michael Johnson", "William Robinson", 
                "David Carter", "Joseph Harris"
            ],
            "F": [
                "Ava Jackson", "Emma Washington", "Sophia Jefferson", 
                "Olivia Brooks", "Maya Scott"
            ]
        }
    }

    # Default name if gender or race is unknown
    default_name = "Taylor Morgan"

    # Get race-based names
    race_names = race_to_name.get(row["MEM_RACE"], {})
    # Get gender-specific names, or use default if not available
    gender_names = race_names.get(row["MEM_GENDER"], [default_name])
    
    # Randomly pick a name from the list
    return random.choice(gender_names)

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

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")

    # Add instructions in the sidebar
    st.sidebar.title("Adding Members")

    st.sidebar.markdown("""
    ### Instructions for Adding Members
    
    Follow these steps to insert data from the **Members** and **Enrollment** [Lokahi dataset](https://lablab.ai/tech/lokahi-hackathon-datasets) into the database table:
    
    ---
    
    #### Step 1: Prepare Your CSV Files
    1. Ensure you have two CSV files:
       - **Members CSV:** Contains columns like `PRIMARY_PERSON_KEY`, `MEMBER_ID`, `MEM_AGE`, and `MEM_MSA_NAME`.
       - **Enrollment CSV:** Contains columns like `PRIMARY_PERSON_KEY`, `MEMBER_ID`, `MEM_GENDER`, `MEM_MSA_NAME`, and `MEM_STATE`.
    2. Verify that:
       - The **PRIMARY_PERSON_KEY**, **MEMBER_ID** and **MEM_MSA_NAME** fields match across both files for the same individual.
       - The **MEM_GENDER** field in the Enrollment CSV is either "M" or "F."
    
    ---
    
    #### Step 2: Paste the CSV Data into the Form
    1. Open the Members CSV file in a text editor.
    2. Copy selected rows of the file (excluding the header row).
    3. Paste the copied content into the **Members** text field in the form below the headers.
    4. Don't overwrite the headers in the web form. If heaaders are overwritten, then refresh the page and redo.
    
    5. Open the Enrollment CSV file in a text editor.
    6. Copy selected rows of the file (excluding the header row).
    7. Paste the copied content into the **Enrollment** text field in the form below the headers.
    
    ---
    
    #### Step 3: Submit the Data
    1. After pasting both CSV contents into the respective fields, click the **Insert Members** button.
    2. The app will process the data, create random names and races, and insert the corresponding records into the database.
    
    ---
    
    #### Step 5: Verify the Data
    1. Confirm the data was successfully inserted into the database by viewing the kūpunas table in the page.
    2. Each record in the `patients` table will include:
       - **Name:** Randomly generated by the system.
       - **Age:** Extracted from the **MEM_AGE** field in the Members CSV.
       - **Gender:** Extracted from the **MEM_GENDER** field in the Enrollment CSV.
       - **Race:** Randomly generated by the system.
    
    ---
    
    """)

    
    st.header('Kūpunas')
    patients_df = fetch_patients()
    ui.table(data=patients_df)
    
    members = """
    PRIMARY_PERSON_KEY,MEMBER_ID,MEMBER_MONTH_START_DATE,YEARMO,MEM_AGE,RELATION,MEM_MSA_NAME,PAYER_LOB,PAYER_TYPE,PROD_TYPE,QTY_MM_MD,QTY_MM_RX,QTY_MM_DN,QTY_MM_VS,MEM_STAT,PRIMARY_CHRONIC_CONDITION_ROLLUP_ID,PRIMARY_CHRONIC_CONDITION_ROLLUP_DESC
    A1B2C3D4E5F6G7H8I9J0K1L2M3N4,A1B2C3D4E5F6G7H8I9J0K1L2M3N4,,,,78,,HONOLULU,,,,,,,,,102.0,SEVERE DEMENTIA
    B2C3D4E5F6G7H8I9J0K1L2M3N4O5,B2C3D4E5F6G7H8I9J0K1L2M3N4O5,,,,72,,KAHULUI,,,,,,,,,102.0,SEVERE DEMENTIA
    C3D4E5F6G7H8I9J0K1L2M3N4O5P6,C3D4E5F6G7H8I9J0K1L2M3N4O5P6,,,,85,,HILO,,,,,,,,,102.0,SEVERE DEMENTIA
    D4E5F6G7H8I9J0K1L2M3N4O5P6Q7,D4E5F6G7H8I9J0K1L2M3N4O5P6Q7,,,,81,,LIHUE,,,,,,,,,102.0,SEVERE DEMENTIA
    E5F6G7H8I9J0K1L2M3N4O5P6Q7R8,E5F6G7H8I9J0K1L2M3N4O5P6Q7R8,,,,79,,WAILUKU,,,,,,,,,102.0,SEVERE DEMENTIA
    F6G7H8I9J0K1L2M3N4O5P6Q7R8S9,F6G7H8I9J0K1L2M3N4O5P6Q7R8S9,,,,68,,KAILUA-KONA,,,,,,,,,102.0,SEVERE DEMENTIA
    G7H8I9J0K1L2M3N4O5P6Q7R8S9T0,G7H8I9J0K1L2M3N4O5P6Q7R8S9T0,,,,74,,WAIMEA,,,,,,,,,102.0,SEVERE DEMENTIA
    H8I9J0K1L2M3N4O5P6Q7R8S9T0U1,H8I9J0K1L2M3N4O5P6Q7R8S9T0U1,,,,76,,LAHAINA,,,,,,,,,102.0,SEVERE DEMENTIA
    I9J0K1L2M3N4O5P6Q7R8S9T0U1V2,I9J0K1L2M3N4O5P6Q7R8S9T0U1V2,,,,70,,PEARL CITY,,,,,,,,,102.0,SEVERE DEMENTIA
    J0K1L2M3N4O5P6Q7R8S9T0U1V2W3,J0K1L2M3N4O5P6Q7R8S9T0U1V2W3,,,,82,,KAPAA,,,,,,,,,102.0,SEVERE DEMENTIA
    """
    members_csv = st.text_area("Members", value=members.strip(), height=300)

    enrollment = """
    PRIMARY_PERSON_KEY,MEMBER_ID,MEM_GENDER,MEM_RACE,MEM_ETHNICITY,MEM_ZIP3,MEM_MSA_NAME,MEM_STATE
    A1B2C3D4E5F6G7H8I9J0K1L2M3N4,A1B2C3D4E5F6G7H8I9J0K1L2M3N4,F,,,968,HONOLULU,HI
    B2C3D4E5F6G7H8I9J0K1L2M3N4O5,B2C3D4E5F6G7H8I9J0K1L2M3N4O5,M,,,967,KAHULUI,HI
    C3D4E5F6G7H8I9J0K1L2M3N4O5P6,C3D4E5F6G7H8I9J0K1L2M3N4O5P6,F,,,967,HILO,HI
    D4E5F6G7H8I9J0K1L2M3N4O5P6Q7,D4E5F6G7H8I9J0K1L2M3N4O5P6Q7,M,,,967,LIHUE,HI
    E5F6G7H8I9J0K1L2M3N4O5P6Q7R8,E5F6G7H8I9J0K1L2M3N4O5P6Q7R8,F,,,967,WAILUKU,HI
    F6G7H8I9J0K1L2M3N4O5P6Q7R8S9,F6G7H8I9J0K1L2M3N4O5P6Q7R8S9,M,,,967,KAILUA-KONA,HI
    G7H8I9J0K1L2M3N4O5P6Q7R8S9T0,G7H8I9J0K1L2M3N4O5P6Q7R8S9T0,F,,,967,WAIMEA,HI
    H8I9J0K1L2M3N4O5P6Q7R8S9T0U1,H8I9J0K1L2M3N4O5P6Q7R8S9T0U1,M,,,967,LAHAINA,HI
    I9J0K1L2M3N4O5P6Q7R8S9T0U1V2,I9J0K1L2M3N4O5P6Q7R8S9T0U1V2,F,,,967,PEARL CITY,HI
    J0K1L2M3N4O5P6Q7R8S9T0U1V2W3,J0K1L2M3N4O5P6Q7R8S9T0U1V2W3,M,,,967,KAPAA,HI
    """
    enrollment_csv = st.text_area("Enrollment", value=enrollment.strip(), height=300)

    insert_members = st.button("Insert Members")
    
    apply_footer()
    
    if insert_members:
        members_df = pd.read_csv(io.StringIO(members_csv))
        enrollment_df = pd.read_csv(io.StringIO(enrollment_csv))

        # Perform the filtering
        filtered_members_df = members_df.merge(
            enrollment_df,
            on=["PRIMARY_PERSON_KEY", "MEM_MSA_NAME"],
            how="inner"
        )
    
        # Merge datasets on PRIMARY_PERSON_KEY
        merged_data = pd.merge(filtered_members_df, enrollment_df, on="PRIMARY_PERSON_KEY", how="inner")
    
        merged_data[["MEM_RACE", "MEM_ETHNICITY"]] = merged_data.apply(assign_race_ethnicity, axis=1)

        if "MEM_GENDER_x" in merged_data.columns and merged_data["MEM_GENDER_x"].notna().any():
            merged_data.rename(columns={"MEM_GENDER_x": "MEM_GENDER"}, inplace=True)
        elif "MEM_GENDER_y" in merged_data.columns and merged_data["MEM_GENDER_y"].notna().any:
            merged_data.rename(columns={"MEM_GENDER_y": "MEM_GENDER"}, inplace=True)
        
        merged_data["NAME"] = merged_data.apply(assign_name, axis=1)

        if "MEM_AGE_x" in merged_data.columns:
            merged_data.rename(columns={"MEM_AGE_x": "MEM_AGE"}, inplace=True)
        elif "MEM_AGE_y" in merged_data.columns:
            merged_data.rename(columns={"MEM_AGE_y": "MEM_AGE"}, inplace=True)

        # Select only the required columns
        final_data = merged_data[["PRIMARY_PERSON_KEY", "NAME", "MEM_AGE", "MEM_GENDER", "MEM_RACE", "MEM_ETHNICITY"]]

        bulk_insert_patient(final_data)
        st.rerun()

if __name__ == "__main__":
    main()
