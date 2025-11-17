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
        
        # --- OSTATECZNA POPRAWKA CZYSZCZENIA ---
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            accords = accord_string.split(",")
            for accord in accords:
                # OSTATECZNA LOGIKA: strip -> strip quotes -> strip AGAIN -> lower
                cleaned_accord = accord.strip().strip("'\"").strip().lower()
                if cleaned_accord: 
                    all_accords_flat_list.append(cleaned_accord)
        
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
            
            score_str = f"{perfume['score']:.2f}"
            st.metric(label="Rating", value=score_str, delta=f"{perfume['ratings']} ratings")
            
            if perfume['main_accords']:
                accords_list = [f"`{acc.strip()}`" for acc in perfume['main_accords'].split(",")]
                st.markdown("**Accords:** " + " ".join(accords_list))

# --- Main Application ---
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    # --- Sidebar ---
    with st.sidebar:
        st.image("https://i.imgur.com/Kz81y1S.png", use_column_width=True)
        st.title("Search Filters")
        
        # Filter 1: Scent Accords
        selected_accords = st.multiselect(
            "Select main accords:",
            options=unique_accords,
            default=[]  # Domyślnie pusta lista
        )

        # Filter 2: Gender
        gender_options = ["Female", "Male", "Unisex"] 
        selected_gender = st.selectbox(
            "Select gender:",
            options=gender_options,
            index=0 
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
    with tab1:
        st.title("Intelligent Perfume Finder")
        st.markdown("Use the filters on the left to find your perfect scent.")

        # Filtering logic
        filtered_df = df[df['gender'] == selected_gender].copy()
        filtered_df = filtered_df[filtered_df['score'] >= min_score]

        if selected_accords:
            # --- OSTATECZNA POPRAWKA CZYSZCZENIA ---
            def contains_all_accords(row_accords_str):
                if pd.isna(row_accords_str):
                    return False
                
                # OSTATECZNA LOGIKA: strip -> strip quotes -> strip AGAIN -> lower
                row_accords_list = [acc.strip().strip("'\"").strip().lower() for acc in row_accords_str.split(",")]
                
                for selected in selected_accords:
                    if selected not in row_accords_list:
                        return False
                return True 

            mask = filtered_df['main_accords'].apply(contains_all_accords)
            filtered_df = filtered_df[mask]

        # Display results
        st.markdown("---")
        st.subheader(f"Found {len(filtered_df)} perfumes matching your criteria:")

        if filtered_df.empty:
            st.warning("No perfumes found matching all criteria. Try relaxing your filters.")
        else:
            num_columns = 3
            cols = st.columns(num_columns)
            
            for index, perfume in enumerate(filtered_df.itertuples()):
                col_index = index % num_columns
                with cols[col_index]:
                    display_perfume_card(perfume)

    # --- Tab 2: Market Statistics ---
    with tab2:
        st.title("Market Statistics & Trends")

        # Chart 1: Rating Distribution (Histogram)
        st.subheader("How are perfume ratings distributed?")
        fig_hist = px.histogram(
            df, 
            x="score", 
            nbins=50, 
            title="Histogram of all perfume ratings",
            labels={"score": "Rating (from 1 to 5)"}
        )
        fig