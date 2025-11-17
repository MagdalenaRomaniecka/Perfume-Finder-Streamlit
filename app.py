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

# --- Custom CSS Function ---
def load_custom_css():
    """Injects custom CSS for a more aesthetic look."""
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

        /* Set font for the entire app */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
        }

        /* Main app background */
        [data-testid="stAppViewContainer"] {
            background-color: #FDF8F5; /* Soft cream/beige */
        }

        /* Sidebar background */
        [data-testid="stSidebar"] {
            background-color: #F5F1EE; /* Slightly darker shade */
            border-right: 1px solid #E0D8D3;
        }

        /* Perfume cards (THE MOST IMPORTANT PART) */
        [data-testid="stVerticalBlockBorder"] {
            background-color: #FFFFFF;
            border-radius: 15px; /* Rounded corners */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* Subtle shadow */
            border: none; /* Remove default border */
            padding: 1.2em !important; /* A bit more internal padding */
        }
        
        /* Image on the card */
        .stImage img {
            border-radius: 10px;
        }

        /* Rating metric */
        [data-testid="stMetric"] {
            background-color: #FAFAFA;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #EEE;
        }

        /* Titles (e.g., "Search Filters") */
        h1, h2, h3 {
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

@st.cache_data
def load_data(filepath, cache_buster_v6): # Cache buster parameter
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
            'url': 'img_link'
        }, inplace=True)
        
        # --- CRITICAL FIX ---
        # Map the CSV gender data (e.g., "for women") to the app's categories (e.g., "Female")
        gender_map = {
            'for women': 'Female',
            'for men': 'Male',
            'for women and men': 'Unisex'
        }
        df['gender'] = df['gender'].map(gender_map)
        
        # Data cleaning: remove rows without key information
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # Convert ratings to numeric type (replacing ',' with '.')
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
        
        # Robust accord cleaning logic
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            # Accords are in "['citrus', 'musky', ...]" format
            # We must strip brackets, quotes, and split
            if isinstance(accord_string, str):
                cleaned_string = accord_string.strip("[]") # Remove brackets
                accords = cleaned_string.split(",")
                for accord in accords:
                    # FINAL LOGIC: strip -> strip quotes -> strip AGAIN -> lower
                    cleaned_accord = accord.strip().strip("'\"").strip().lower()
                    if cleaned_accord: 
                        all_accords_flat_list.append(cleaned_accord)
        
        unique_accords = sorted(list(set(all_accords_flat_list)))
        
        return df, unique_accords
        
    except FileNotFoundError:
        st.error(f"Error: Data file not found at path: {filepath}.")
        st.error(f"Please make sure the `fra_perfumes.csv` file is in the same folder as `app.py`.")
        return None, []
    except KeyError as e:
        st.error(f"Critical Error: Expected columns not found in CSV file: {e}")
        st.error("Please check if your `fra_perfumes.csv` file contains the columns: 'Name', 'Gender', 'Rating Value', 'Rating Count', 'Main Accords', 'url'.")
        return None, []
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
        return None, []

def display_perfume_card(perfume):
    """Displays a single perfume card in the gallery."""
    
    # We are using .itertuples() in the main loop,
    # so we must use dot notation (perfume.name).
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if perfume.img_link and isinstance(perfume.img_link, str):
                st.image(perfume.img_link, use_column_width=True)
            else:
                st.image("https://placehold.co/200x200/eee/ccc?text=No+Image", use_column_width=True)

        with col2:
            st.markdown(f"**{perfume.name}**")
            
            score_str = f"{perfume.score:.2f}"
            st.metric(label="Rating", value=score_str, delta=f"{perfume.ratings} ratings")
            
            if perfume.main_accords:
                # Logic for accords stored as a string "['a','b']"
                if isinstance(perfume.main_accords, str):
                    cleaned_string = perfume.main_accords.strip("[]")
                    accords_list_raw = cleaned_string.split(",")
                else:
                    accords_list_raw = [] # Fallback for unexpected data type

                accords_list_clean = []
                for acc in accords_list_raw:
                    cleaned_accord = acc.strip().strip("'\"").strip()
                    if cleaned_accord:
                        accords_list_clean.append(f"`{cleaned_accord}`")
                
                st.markdown("**Accords:** " + " ".join(accords_list_clean))

# --- Main Application ---

# Load the custom CSS styles
load_custom_css()

# Load the data (with cache buster)
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v6="v6") # v6 cache buster

if df is not None:
    # --- Sidebar ---
    with st.sidebar:
        st.title("Search Filters")
        
        # Filter 1: Scent Accords
        selected_accords = st.multiselect(
            "Select main accords:",
            options=unique_accords,
            default=[]  # Default to empty list to show all results
        )

        # Filter 2: Gender
        # These options now match our MAPPED data
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
        st.info("Project by Magdalena Romaniecka. Data from Kaggle.")

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
            # Robust accord filtering function
            def contains_all_accords(row_accords_str):
                if pd.isna(row_accords_str):
                    return False
                
                # FINAL LOGIC: strip -> strip quotes -> strip AGAIN -> lower
                row_accords_list = []
                cleaned_string = row_accords_str.strip("[]")
                accords = cleaned_string.split(",")
                for accord in accords:
                    cleaned_accord = accord.strip().strip("'\"").strip().lower()
                    if cleaned_accord:
                        row_accords_list.append(cleaned_accord)
                
                # Check if all selected accords are in this row's list
                for selected in selected_accords:
                    if selected not in row_accords_list:
                        return False
                return True # Only returns True if all selected accords are found

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
        fig_hist.update_layout(bargap=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)

        # Chart 2: Most popular accords (Bar chart)
        st.subheader("Top 15 Most Common Scent Accords")
        
        # Robust accord cleaning logic (for chart)
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            cleaned_string = accord_string.strip("[]")
            accords = cleaned_string.split(",")
            for accord in accords:
                # Final logic: strip -> strip quotes -> strip AGAIN -> lower
                cleaned_accord = accord.strip().strip("'\"").strip().lower()
                if cleaned_accord:
                    all_accords_flat_list.append(cleaned_accord)
        
        accords_counts = pd.Series(all_accords_flat_list).value_counts()
        top_15_accords = accords_counts.head(15).sort_values(ascending=True)

        fig_bar = px.bar(
            top_15_accords,
            x=top_15_accords.values,
            y=top_15_accords.index,
            orientation='h',
            title="Top 15 Accords in the database",
            labels={"x": "Number of occurrences", "y": "Accord"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.header("Application could not be started.")
    st.warning("Please resolve the data loading issue to continue.")