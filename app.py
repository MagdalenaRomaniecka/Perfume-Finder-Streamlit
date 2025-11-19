import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS: Mobile-First, High Contrast, Luxury Design ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        /* --- GLOBAL DARK THEME --- */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #050505; /* Deepest Black */
        }
        [data-testid="stAppViewContainer"] { background-color: #050505; }
        
        /* --- HIDE DEFAULT STREAMLIT HEADER & SIDEBAR --- */
        header { visibility: hidden; }
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none; }
        
        /* Adjust top padding since header is gone */
        .block-container { padding-top: 2rem !important; }

        /* --- HIGH CONTRAST INPUTS --- */
        
        /* Widget Labels */
        label p {
            color: #D4AF37 !important; /* Gold */
            font-size: 13px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Radio Buttons (Gender) */
        div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important; /* Bright White Text */
            font-weight: 500 !important;
        }
        div[role="radiogroup"] div[data-baseweb="radio"] div {
            border-color: #D4AF37 !important;
        }
        div[role="radiogroup"] [aria-checked="true"] div[data-baseweb="radio"] div {
            background-color: #D4AF37 !important;
        }
        
        /* Slider (Rating) */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important; /* Bright White Numbers */
            font-weight: 600 !important;
        }
        div[data-testid="stSlider"] div[data-baseweb="slider"] div {
            background-color: #D4AF37 !important;
        }

        /* Multiselect (Notes) */
        .stMultiSelect div[data-baseweb="select"] span {
            color: #FFFFFF !important;
        }
        div[role="listbox"] ul {
            background-color: #1A1A1A !important;
        }
        div[role="listbox"] li {
            color: white !important;
            background-color: #1A1A1A !important;
        }

        /* --- EXPANDER STYLING --- */
        .streamlit-expanderHeader {
            background-color: #111111 !important;
            border: 1px solid #333 !important;
            color: #D4AF37 !important;
            font-family: 'Montserrat', sans-serif;
            border-radius: 5px;
        }
        
        /* --- PERFUME CARD STYLING --- */
        .perfume-card {
            background-color: #121212;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            padding: 20px 0;
            margin-bottom: 0;
        }
        
        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFFFFF;
            font-weight: 600;
            margin-bottom: 5px;
            line-height: 1.2;
        }

        .p-rating {
            font-size: 12px;
            color: #D4AF37; 
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .p-notes {
            font-size: 11px;
            color: #888888;
            margin-top: 6px;
            line-height: 1.4;
        }

        .p-link {
            font-size: 10px;
            color: #555;
            text-decoration: none;
            margin-left: 10px;
            border: 1px solid #333;
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 10px;
        }

        /* --- HEADER TYPOGRAPHY --- */
        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: 28px;
            color: #D4AF37;
            text-align: center;
            margin-bottom: 5px;
            font-weight: 700;
        }
        .sub-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 10px;
            color: #666;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading & Processing ---
@st.cache_data
def load_data(filepath): 
    try:
        df = pd.read_csv(filepath)
        # Standardize column names
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # 1. Fix concatenated names (e.g., remove 'for women' from name string)
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
        
        # 2. Standardize Gender Categories
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # 3. Remove incomplete rows
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # 4. Ensure numeric score
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # 5. Extract and clean unique accords for filter list
        all_accords = set()
        for accords_str in df['main_accords'].dropna():
            if isinstance(accords_str, str):
                # Clean artifacts like brackets and quotes
                raw_list = accords_str.replace("[", "").replace("]", "").replace("'", "").replace('"', "").split(",")
                for item in raw_list:
                    clean_item = item.strip().lower()
                    if clean_item: all_accords.add(clean_item)
        
        return df, sorted(list(all_accords))
    except Exception:
        return None, []

def render_card(perfume):
    """Renders a clean HTML card for the perfume."""
    notes_str = ""
    if isinstance(perfume.main_accords, str):
        # Clean notes string for display
        raw = perfume.main_accords.replace("[", "").replace("]", "").replace("'", "").replace('"', "").split(",")
        clean = [n.strip().strip("'\"").strip().lower() for n in raw[:4] if n.strip()]
        notes_str = ", ".join(clean)

    html = f"""
    <div class="perfume-card">
        <div style="display:flex; justify-content:space-between;">
            <div class="p-name">{perfume.name}</div>
            <div class="p-rating">★ {perfume.score:.1f}</div>
        </div>
        <div class="p-notes">{notes_str}</div>
        <div style="text-align:right;">
            <a href="{perfume.img_link}" target="_blank" class="p-link">VIEW DETAILS ↗</a>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Application Logic ---
load_custom_css()
# Added dummy parameter to force cache invalidation for this version
df, unique_accords = load_data("fra_perfumes.csv") 

if df is not None:
    
    # --- Header ---
    st.markdown('<div class="main-title">PERFUME FINDER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">LUXURY DATABASE</div>', unsafe_allow_html=True)
    
    # --- Filter Section ---
    with st.expander("⚡ FILTERS", expanded=True):
        # Gender Selection
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], horizontal=True)
        st.write("")
        
        # Rating Selection
        score = st.slider("MIN RATING", 1.0, 5.0, 4.0, 0.1)
        st.write("")
        
        # Ingredient Selection
        notes = st.multiselect("NOTES", unique_accords, placeholder="Select ingredients...")
        
    # --- Filtering Engine ---
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_str):
            if pd.isna(row_str): return False
            row_clean = row_str.replace("[", "").replace("]", "").replace("'", "").replace('"', "").lower()
            return all(note in row_clean for note in notes)
        filtered = filtered[filtered['main_accords'].apply(check_notes)]

    # --- Results Display ---
    st.write("")
    st.markdown(f"<div style='text-align: center; color: #666; font-size: 11px; margin-bottom: 20px;'>FOUND {len(filtered)} RESULTS</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        # Limit results for performance
        for row in filtered.head(40).itertuples():
            render_card(row)
            
    st.markdown("<br><br><div style='text-align: center; color: #333; font-size: 10px;'>© 2024 Portfolio Project</div>", unsafe_allow_html=True)
else:
    st.error("Data Error: Could not load dataset.")