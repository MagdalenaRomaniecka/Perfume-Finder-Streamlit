import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
# Layout set to 'centered' for better mobile experience and blog-like feel
st.set_page_config(
    page_title="Perfume Finder 🔎",
    page_icon="👃",
    layout="centered",
    initial_sidebar_state="collapsed" # Zmieniono na 'collapsed', bo filtry są w środku!
)

# --- Custom CSS Function ---
def load_custom_css():
    """Wstrzykuje niestandardowy CSS dla luksusowego ciemnego motywu."""
    st.markdown("""
        <style>
        /* Import Google Fonts: Playfair Display (dla tytułów) i Montserrat (dla tekstu) */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght=700&family=Playfair+Display:wght@700&display=swap');

        /* Global font settings */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #FAFAFA; /* Jasny tekst dla ciemnego tła */
        }

        /* Main App Background - Dark Onyx */
        [data-testid="stAppViewContainer"] {
            background-color: #1A1A1A;
        }

        /* USUNIĘTO SIDEBAR CSS - Sidebar będzie teraz ciemny z automatu, ale jest schowany */
        [data-testid="stSidebar"] {
            background-color: #222222 !important; /* Upewniamy się, że jest ciemny, mimo że go ukryliśmy */
            border-right: 1px solid #333333;
        }


        /* Karty perfum */
        [data-testid="stVerticalBlockBorder"] {
            background-color: #2A2A2A; 
            border-radius: 12px;
            border: 1px solid #3A3A3A; 
            padding: 20px !important;
        }
        
        /* Obrazek na karcie */
        .stImage img {
            border-radius: 8px;
        }

        /* Metryka oceny (Rating) */
        [data-testid="stMetric"] {
            background-color: #333333;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #444444;
        }

        /* Tytuły (H1, H2, H3) - nowa, luksusowa czcionka */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            color: #FFFFFF; 
            letter-spacing: 0.5px;
        }

        /* Złote linki */
        a {
            color: #D4AF37 !important; 
            text-decoration: none;
            font-weight: 600;
        }
        a:hover {
            text-decoration: underline;
            color: #F4CF57 !important; 
        }

        /* Poprawki dla widgetów Streamlit, aby pasowały do ciemnego motywu */
        [data-testid="stSelectbox"] div, [data-testid="stMultiselect"] div {
            background-color: #2A2A2A;
            color: white;
        }

        /* Zmień kolor czcionki inputów (rozwiąże problem "lania się" na jasnym tle w inputach) */
        .stMultiSelect, .stSelectbox {
             color: white; 
        }
        </style>
    """, unsafe_allow_html=True)

# --- Helper Functions (Same, poprawne funkcje co ostatnio) ---
@st.cache_data
def load_data(filepath, cache_buster_final): # v11 - Nowy cache buster
    """Loads, cleans, and preprocesses data from the CSV file."""
    try:
        df = pd.read_csv(filepath)
        
        # 1. Rename columns to match internal logic
        df.rename(columns={
            'Name': 'name',
            'Gender': 'gender',
            'Rating Value': 'score',
            'Rating Count': 'ratings',
            'Main Accords': 'main_accords',
            'url': 'img_link'
        }, inplace=True)
        
        # 2. Fix "Glued" Names (Remove gender text from name)
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], 
                axis=1
            )

        # 3. Map Gender Data to Clean Categories
        gender_map = {
            'for women': 'Female',
            'for men': 'Male',
            'for women and men': 'Unisex'
        }
        df['gender'] = df['gender'].map(gender_map)
        
        # 4. Remove incomplete rows
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # 5. Convert scores to numbers
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
        
        # 6. Robust Accord Cleaning (Fixes double quotes and spaces)
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            if isinstance(accord_string, str):
                cleaned_string = accord_string.strip("[]") 
                accords = cleaned_string.split(",")
                for accord in accords:
                    cleaned_accord = accord.strip().strip("'\"").strip().lower()
                    if cleaned_accord: 
                        all_accords_flat_list.append(cleaned_accord)
        
        unique_accords = sorted(list(set(all_accords_flat_list)))
        
        return df, unique_accords
        
    except FileNotFoundError:
        st.error("Error: Data file not found. Please ensure `fra_perfumes.csv` is in the directory.")
        return None, []
    except KeyError as e:
        st.error(f"Critical Error: Missing columns in CSV: {e}")
        return None, []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None, []

def display_perfume_card(perfume):
    """Displays a single perfume card in the UI."""
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://placehold.co/200x200/2A2A2A/666?text=Perfume", use_column_width=True) 
            
            if perfume.img_link and isinstance(perfume.img_link, str):
                st.markdown(f"<div style='text-align: center; margin-top: 10px;'><a href='{perfume.img_link}' target='_blank'>View on Fragrantica ↗</a></div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"### {perfume.name}")
            
            st.metric(label="Rating", value=f"{perfume.score:.2f}", delta=f"{perfume.ratings} votes")
            
            if perfume.main_accords:
                if isinstance(perfume.main_accords, str):
                    cleaned_string = perfume.main_accords.strip("[]")
                    accords_list_raw = cleaned_string.split(",")
                else:
                    accords_list_raw = []

                accords_list_clean = []
                for acc in accords_list_raw:
                    cleaned_accord = acc.strip().strip("'\"").strip()
                    if cleaned_accord:
                        accords_list_clean.append(f"`{cleaned_accord}`")
                
                st.markdown("**Notes:** " + " ".join(accords_list_clean[:5])) 

# --- Main Application Logic ---

# 1. Load CSS
load_custom_css()

# 2. Load Data (v11 forces a final cache refresh)
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_final="v11")

if df is not None:
    # --- Główny kontener filtrów (Teraz na górze!) ---
    st.header("Luxury Perfume Finder") # ZMIENIONO: st.title na st.header, aby zmniejszyć rozmiar
    st.markdown("Find your signature scent instantly.")
    
    st.markdown("---")
    st.subheader("Filter Your Search")

    # Używamy st.columns, aby filtry były obok siebie na dużym ekranie
    col_gender, col_score, col_accords = st.columns([1, 1, 2]) 
    
    with col_gender:
        gender_options = ["Female", "Male", "Unisex"] 
        selected_gender = st.selectbox(
            "Select Gender:",
            options=gender_options,
            index=0 
        )

    with col_score:
        min_score = st.slider(
            "Minimum Rating:",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.1
        )

    with col_accords:
        selected_accords = st.multiselect(
            "Select Scent Notes:",
            options=unique_accords,
            default=[]  
        )

    st.markdown("---")
    
    # --- Tab 1: Finder ---
    tab1, tab2 = st.tabs(["**🔎 Perfume Finder**", "**📊 Market Analysis**"])

    with tab1:
        # Filtering Logic (Taka sama, ale filtry są zdefiniowane wyżej)
        filtered_df = df[df['gender'] == selected_gender].copy()
        filtered_df = filtered_df[filtered_df['score'] >= min_score]

        if selected_accords:
            def contains_all_accords(row_accords_str):
                if pd.isna(row_accords_str): return False
                
                row_accords_list = []
                cleaned_string = row_accords_str.strip("[]")
                accords = cleaned_string.split(",")
                for accord in accords:
                    cleaned_accord = accord.strip().strip("'\"").strip().lower()
                    if cleaned_accord:
                        row_accords_list.append(cleaned_accord)
                
                for selected in selected_accords:
                    if selected not in row_accords_list: return False
                return True 

            mask = filtered_df['main_accords'].apply(contains_all_accords)
            filtered_df = filtered_df[mask]

        # Results
        st.subheader(f"Found {len(filtered_df)} exclusive matches:")

        if filtered_df.empty:
            st.info("No perfumes found matching these exact criteria. Try removing some note filters.")
        else:
            # Cards are displayed one under the other (ideal for centered layout)
            for index, perfume in enumerate(filtered_df.itertuples()):
                display_perfume_card(perfume)

    # --- Tab 2: Statistics ---
    with tab2:
        st.title("Market Insights")
        st.markdown("Analysis of trends across the database.")

        # Chart 1
        st.markdown("### Rating Distribution")
        fig_hist = px.histogram(
            df, x="score", nbins=50, 
            title="",
            labels={"score": "Rating"},
            template="plotly_dark", 
            color_discrete_sequence=['#D4AF37'] 
        )
        fig_hist.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

        # Chart 2
        st.markdown("### Top 15 Scent Notes")
        
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            cleaned_string = accord_string.strip("[]")
            accords = cleaned_string.split(",")
            for accord in accords:
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
            title="",
            labels={"x": "Count", "y": "Note"},
            template="plotly_dark",
            color_discrete_sequence=['#D4AF37'] 
        )
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.caption("© 2024 Magdalena Romaniecka. Code built with Streamlit.")
else:
    st.error("Application failed to load data.")