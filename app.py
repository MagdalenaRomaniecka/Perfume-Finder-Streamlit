import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS: Ultra-Clean Mobile (No Header, High Contrast) ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        /* --- GLOBAL DARK THEME --- */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #050505;
        }
        [data-testid="stAppViewContainer"] { background-color: #050505; }
        
        /* --- AGGRESSIVE HEADER REMOVAL --- */
        /* This hides the top bar with hamburger menu, 'deploy', and 'keyboard' icons */
        header { visibility: hidden; }
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        
        /* Move content up to fill the gap left by header */
        .block-container { padding-top: 1rem !important; }

        /* --- INPUT VISIBILITY (GOLD & WHITE) --- */
        
        /* Labels */
        label p {
            color: #D4AF37 !important; /* Gold */
            font-size: 13px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Radio Buttons (Gender) */
        div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important; /* White Text */
            font-weight: 500 !important;
        }
        /* Selected Radio Button Dot */
        div[role="radiogroup"] div[data-baseweb="radio"] div {
            border-color: #D4AF37 !important;
        }
        div[role="radiogroup"] [aria-checked="true"] div[data-baseweb="radio"] div {
            background-color: #D4AF37 !important;
        }
        
        /* Slider */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
        }
        div[data-testid="stSlider"] div[data-baseweb="slider"] div {
            background-color: #D4AF37 !important;
        }

        /* Multiselect */
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

        /* --- EXPANDER (FILTER BOX) --- */
        .streamlit-expanderHeader {
            background-color: #111111 !important;
            border: 1px solid #333 !important;
            color: #D4AF37 !important;
            font-family: 'Montserrat', sans-serif;
            border-radius: 0px; /* Clean corners */
        }
        
        /* --- CARD STYLING --- */
        .perfume-card {
            background-color: #121212;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            padding: 15px 0;
            margin-bottom: 0;
        }
        
        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFFFFF;
            font-weight: 600;
            margin-bottom: 4px;
            line-height: 1.2;
        }

        .p-rating {
            font-size: 12px;
            color: #D4AF37; 
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .p-notes {
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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
        }

        /* --- TITLE STYLING --- */
        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: 26px; /* Compact Title */
            color: #D4AF37;
            text-align: center;
            margin-bottom: 2px;
            font-weight: 700;
        }
        .sub-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 10px;
            color: #666;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v26): # v26 Cache Buster
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
            
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
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

def render_minimal_card(perfume):
    """Renders a very clean, text-based card."""
    notes_str = ""
    if isinstance(perfume.main_accords, str):
        raw = perfume.main_accords.strip("[]").split(",")
        clean = [n.strip().strip("'\"").strip().lower() for n in raw[:4]]
        notes_str = ", ".join(clean)

    html = f"""
    <div class="perfume-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="p-name">{perfume.name}</div>
            <div class="p-rating">★ {perfume.score:.1f}</div>
        </div>
        <div class="p-notes">{notes_str}</div>
        <div style="text-align: right; margin-top: 8px;">
            <a href="{perfume.img_link}" target="_blank" style="text-decoration: none; color: #D4AF37; font-size: 10px; font-weight: 600;">DETAILS ↗</a>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v26="v26")

if df is not None:
    
    # --- HEADER ---
    st.markdown('<div class="main-title">Perfume Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Luxury Database</div>', unsafe_allow_html=True)
    
    # --- FILTERS ---
    # Simple expander for clean look
    with st.expander("🎛️ FILTERS", expanded=True):
        
        # Gender
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], horizontal=True)
        
        st.write("")
        
        # Score
        score = st.slider("MIN RATING", 1.0, 5.0, 4.0, 0.1)
        
        st.write("")

        # Notes
        notes = st.multiselect("NOTES", unique_accords, placeholder="Search ingredients...")
        
    # --- FILTERING ---
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

    # --- RESULTS ---
    st.write("")
    st.markdown(f"<div style='text-align: center; color: #666; font-size: 11px; letter-spacing: 1px; margin-bottom: 20px;'>FOUND {len(filtered)} RESULTS</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        # Limit to 40 for performance
        for row in filtered.head(40).itertuples():
            render_minimal_card(row)
            
    st.markdown("<br><br><div style='text-align: center; color: #333; font-size: 10px;'>© 2024</div>", unsafe_allow_html=True)

else:
    st.error("System Error.")