import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS: Full Screen Mode & Luxury Design ---
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
        
        /* --- CRITICAL FIX: HIDE TOP HEADER BAR --- */
        /* This removes the 'Keyboard'/'Menu' bar completely for a clean look */
        [data-testid="stHeader"] {
            display: none;
        }
        /* Move content up since header is gone */
        .block-container {
            padding-top: 2rem !important;
        }

        /* HIDE SIDEBAR ELEMENTS COMPLETELY */
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none; }

        /* --- AESTHETIC FRAMED HEADER --- */
        .luxury-frame {
            border: 2px solid #D4AF37; /* Gold Border */
            padding: 20px;
            border-radius: 0px;
            text-align: center;
            margin-bottom: 20px;
            background-color: #111;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
        }
        
        .luxury-title {
            font-family: 'Playfair Display', serif;
            font-size: 32px !important; /* Optimized for mobile */
            color: #D4AF37; /* Gold */
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .luxury-subtitle {
            font-family: 'Montserrat', sans-serif;
            font-size: 12px;
            color: #FFFFFF;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 5px;
        }

        /* --- INPUT VISIBILITY FIXES --- */
        
        /* Radio Buttons (Gender) */
        div[role="radiogroup"] label {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            padding: 8px 12px !important;
            border-radius: 4px !important;
            margin-right: 5px !important;
        }
        div[role="radiogroup"] label p {
            color: #FFFFFF !important; 
            font-weight: 600 !important;
            font-size: 14px !important;
        }

        /* Slider (Rating) */
        div[data-testid="stSlider"] label p {
            color: #D4AF37 !important; 
            font-size: 14px !important;
            font-weight: 600 !important;
        }
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
        }

        /* Multiselect (Notes) */
        .stMultiSelect label p {
            color: #D4AF37 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
        }
        .stMultiSelect span[data-baseweb="tag"] {
            background-color: #D4AF37 !important;
            color: black !important;
        }
        div[role="listbox"] ul li {
            color: white !important;
            background-color: #252525 !important;
        }
        
        /* --- PERFUME CARD STYLING --- */
        .perfume-card {
            background-color: #121212;
            border: 1px solid #333;
            border-left: 4px solid #D4AF37; 
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        }
        
        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 20px; 
            color: #FFFFFF;
            font-weight: 700;
            margin-bottom: 5px;
            line-height: 1.2;
        }

        .p-rating {
            font-size: 13px;
            color: #D4AF37; 
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .p-notes {
            font-size: 11px;
            color: #AAAAAA;
            font-style: italic;
            margin-top: 6px;
            line-height: 1.4;
        }

        .p-link {
            display: inline-block;
            margin-top: 12px;
            font-size: 10px;
            color: #000;
            background-color: #D4AF37; 
            padding: 6px 12px;
            text-decoration: none;
            font-weight: 700;
            letter-spacing: 1px;
            border-radius: 2px;
        }
        
        /* Expander Styling */
        .streamlit-expanderHeader {
            font-family: 'Montserrat', sans-serif;
            font-size: 14px;
            color: #FFFFFF !important;
            background-color: #1A1A1A !important;
            border: 1px solid #D4AF37 !important;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v19): # v19 Cache Buster
    try:
        df = pd.read_csv(filepath)
        # Column renaming
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Fix glued names
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
            
        # Map genders
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # Cleanup
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # Convert score
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # Extract unique accords
        all_accords = set()
        for accords_str in df['main_accords'].dropna():
            if isinstance(accords_str, str):
                raw_list = accords_str.strip("[]").split(",")
                for item in raw_list:
                    clean_item = item.strip().strip("'\"").strip().lower()
                    if clean_item: all_accords.add(clean_item)
        
        return df, sorted(list(all_accords))
    except Exception:
        return None, []

def render_luxury_card(perfume):
    """Renders a high-end, text-focused perfume card."""
    
    notes_str = ""
    if isinstance(perfume.main_accords, str):
        raw = perfume.main_accords.strip("[]").split(",")
        clean = [n.strip().strip("'\"").strip().lower() for n in raw[:5]] 
        notes_str = " • ".join(clean)

    html = f"""
    <div class="perfume-card">
        <div class="p-name">{perfume.name}</div>
        <div class="p-rating">★ {perfume.score:.2f} / 5.0</div>
        <div class="p-notes">{notes_str}</div>
        <a href="{perfume.img_link}" target="_blank" class="p-link">DETAILS ↗</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v19="v19")

if df is not None:
    
    # --- FRAMED HEADER (Pure HTML) ---
    st.markdown("""
        <div class="luxury-frame">
            <h1 class="luxury-title">Perfume Finder</h1>
            <div class="luxury-subtitle">Luxury Database</div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- FILTERS (Shortened Labels to prevent wrapping) ---
    with st.expander("▼ FILTERS ▼", expanded=True):
        
        st.write("")
        # Gender (Radio with All option)
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], horizontal=True)
        
        st.write("")
        st.markdown("<hr style='border-color: #333; margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Score
        score = st.slider("MIN RATING", 1.0, 5.0, 4.0, 0.1)
        
        st.write("")
        st.markdown("<hr style='border-color: #333; margin: 10px 0;'>", unsafe_allow_html=True)

        # Notes
        notes = st.multiselect("NOTES", unique_accords, placeholder="e.g. rose...")
        
    # --- FILTERING LOGIC ---
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_str):
            if pd.isna(row_str): return False
            row_list = [n.strip().strip("'\"").strip().lower() for n in row_str.strip("[]").split(",")]
            return all(note in row_list for note in notes)
        filtered = filtered[filtered['main_accords'].apply(check_notes)]

    # --- RESULTS DISPLAY ---
    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: #D4AF37; letter-spacing: 2px; margin-bottom: 20px; font-size: 12px;'>FOUND {len(filtered)} MATCHES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        for row in filtered.head(50).itertuples():
            render_luxury_card(row)
            
    st.markdown("<br><br><div style='text-align: center; color: #444; font-size: 10px;'>© 2024 Portfolio Project</div>", unsafe_allow_html=True)

else:
    st.error("System Error.")