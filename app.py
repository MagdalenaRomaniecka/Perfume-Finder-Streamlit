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
        
        # Extract unique accords
        all_accords_str = ",".join(df['main_accords'].unique())
        # Fix: convert all accords to lowercase
        all_accords_list = [accord.strip().lower() for accord in all_accords_str.split(",")]
        unique_accords = sorted(list(set(all_accords_list)))
        
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
    with tab1:
        st.title("Intelligent Perfume Finder")
        st.markdown("Use the filters on the left to find your perfect scent.")

        # Filtering logic
        filtered_df = df[df['gender'] == selected_gender].copy()
        filtered_df = filtered_df[filtered_df['score'] >= min_score]

        if selected_accords:
            def contains_all_accords(row_accords):
                if pd.isna(row_accords):
                    return False
                # Convert row accords to lower for comparison
                row_accords_lower = row_accords.lower()
                for accord in selected_accords:
                    if accord not in row_accords_lower:
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
        fig_hist.update_layout(bargap=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)

        # Chart 2: Most popular accords (Bar chart)
        st.subheader("Top 15 Most Common Scent Accords")
        
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            # Use .lower() to count "Vanilla" and "vanilla" as the same
            all_accords_flat_list.extend([acc.strip().lower() for acc in accord_string.split(",")])
        
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