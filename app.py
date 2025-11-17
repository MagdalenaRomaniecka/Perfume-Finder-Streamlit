import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder 🔎",
    page_icon="👃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---

@st.cache_data
def load_data(filepath):
    """Loads and preprocesses data from a CSV file."""
    try:
        df = pd.read_csv(filepath)
        
        # Translate column names from your CSV file to the ones the app uses
        df.rename(columns={
            'Name': 'name',
            'Gender': 'gender',
            'Rating Value': 'score',
            'Rating Count': 'ratings',
            'Main Accords': 'main_accords',
            'url': 'img_link'  # Assuming the image link column is named 'url'
        }, inplace=True)
        
        # Data cleaning: remove rows without key information
        df.dropna(subset=['main_accords', 'name', 'img_link'], inplace=True)
        
        # Convert ratings to numeric type (replacing ',' with '.')
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
        
        # --- POPRAWKA 1: Solidne czyszczenie akordów ---
        # Tworzymy płaską listę wszystkich akordów ze wszystkich wierszy
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            accords = accord_string.split(",")
            for accord in accords:
                # Czyścimy spacje ORAZ cudzysłowy i zamieniamy na małe litery
                cleaned_accord = accord.strip().strip("'\"").lower()
                if cleaned_accord: # Unikamy dodawania pustych stringów
                    all_accords_flat_list.append(cleaned_accord)
        
        # Tworzymy unikalną, posortowaną listę z czystych danych
        unique_accords = sorted(list(set(all_accords_flat_list)))
        
        return df, unique_accords
        
    except FileNotFoundError:
        st.error(f"Error: Data file not found at path: {filepath}.")
        st.error(f"Please make sure the `fra_perfumes.csv` file is in the same folder as `app.py`.")
        st.info("Download the file from: https://www.kaggle.com/datasets/olgagmiufana1/fragrantica-com-fragrance-dataset")
        return None, []
    except KeyError as e:
        st.error(f"Critical Error: Expected columns not found in CSV file: {e}")
        st.error("Please check if your `fra_perfumes.csv` file contains the columns: 'Name', 'Gender', 'Rating Value', 'Rating Count', 'Main Accords', 'url'.")
        st.info("If your columns are named differently, we need to update the `df.rename()` block in the code.")
        return None, []
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
        return None, []

def display_perfume_card(perfume):
    """Displays a single perfume card in the gallery."""
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if perfume['img_link'] and isinstance(perfume['img_link'], str):
                st.image(perfume['img_link'], use_column_width=True)
            else:
                st.image("https://placehold.co/200x200/eee/ccc?text=No+Image", use_column_width=True)

        with col2:
            st.markdown(f"**{perfume['name']}**")
            
            # Your CSV file doesn't have a 'brand' column, so we removed it to avoid errors
            # st.markdown(f"*{perfume['brand']}*") 
            
            score_str = f"{perfume['score']:.2f}"
            st.metric(label="Rating", value=score_str, delta=f"{perfume['ratings']} ratings")
            
            if perfume['main_accords']:
                accords_list = [f"`{acc.strip()}`" for acc in perfume['main_accords'].split(",")]
                st.markdown("**Accords:** " + " ".join(accords_list))

# --- Main Application ---

# Load data
df, unique_accords = load_data("fra_perfumes.csv")

# Check if data was loaded successfully
if df is not None:

    # --- Sidebar ---
    with st.sidebar:
        st.image("https://i.imgur.com/Kz81y1S.png", use_column_width=True)
        st.title("Search Filters")

        # Check which of the default values ACTUALLY exist in the data
        desired_defaults = ["vanilla", "sweet", "powdery"]
        # Use only those that exist to avoid errors
        actual_defaults = [d for d in desired_defaults if d in unique_accords]

        # Filter 1: Scent Accords
        selected_accords = st.multiselect(
            "Select main accords:",
            options=unique_accords,
            default=actual_defaults  # Changed to use safe defaults
        )

        # Filter 2: Gender
        # The options MUST match the data in your 'Gender' column from the CSV
        gender_options = ["Female", "Male", "Unisex"] 
        selected_gender = st.selectbox(
            "Select gender:",
            options=gender_options,
            index=0  # Defaults to 'Female'
        )

        # Filter 3: Minimum rating
        min_score = st.slider(
            "Minimum rating (1.0 - 5.0):",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.1
        )
        
        st.markdown("---")
        st.info("Project created by Magdalena Romaniecka. Data from Kaggle.")

    # --- Main Page Content ---
    
    tab1, tab2 = st.tabs(["**🔎 Find Perfumes**", "**📊 Market Statistics**"])

    # --- Tab 1: Perfume Finder ---