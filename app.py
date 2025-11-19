import streamlit as st
import pandas as pd
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CSS: Modern Chips, Clean Text, High Visibility Slider ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        /* --- GLOBAL DARK THEME --- */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #0E0E0E; 
        }
        [data-testid="stAppViewContainer"] { background-color: #0E0E0E; }
        [data-testid="stHeader"] { display: none; } /* Hide Header */
        
        /* --- SIDEBAR STYLING --- */
        section[data-testid="stSidebar"] {
            background-color: #111; 
            border-right: 1px solid #333;
        }
        
        /* Sidebar Headers */
        .sidebar-header {
            color: #D4AF37;
            font-family: 'Montserrat', sans-serif; /* Clean font for labels */
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        /* --- MODERN "CHIPS" (PILLS) FOR GENDER SELECTION --- */
        /* Zamieniamy zwykłe Radio Buttons na nowoczesne "Pastylki" */
        
        div[role="radiogroup"] {
            flex-direction: row; /* Align horizontally */
            gap: 8px;
            flex-wrap: wrap;
        }
        
        div[role="radiogroup"] label {
            background-color: transparent !important;
            border: 1px solid #444 !important;
            border-radius: 20px !important; /* Rounded Pill Shape */
            padding: 6px 16px !important;
            margin: 0 !important;
            transition: all 0.2s ease;
            width: auto !important;
            flex: 1; /* Distribute space evenly */
            display: flex;
            justify-content: center;
        }
        
        div[role="radiogroup"] label:hover {
            border-color: #D4AF37 !important;
            cursor: pointer;
        }

        div[role="radiogroup"] label p {
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #AAA !important;
        }

        /* SELECTED STATE (High Visibility) */
        div[role="radiogroup"] label:has(input:checked) {
            background-color: #D4AF37 !important; /* Gold Fill */
            border-color: #D4AF37 !important;
        }
        div[role="radiogroup"] label:has(input:checked) p {
            color: #000000 !important; /* Black Text */
            font-weight: 700 !important;
        }
        
        /* Hide the default radio circle */
        div[role="radiogroup"] label div[data-baseweb="radio"] { display: none; }


        /* --- VISIBLE SLIDER --- */
        div[data-testid="stSlider"] {
            padding-top: 10px;
        }
        /* The numbers above the slider */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
            font-size: 14px;
            font-weight: 700;
        }
        /* The slider track */
        div[data-testid="stSlider"] .st-ae {
            background-color: #D4AF37 !important; /* Gold Track */
        }
        /* The thumb (handle) */
        div[data-testid="stSlider"] div[role="slider"] {
            background-color: #FFF !important; /* White Handle */
            border: 2px solid #D4AF37 !important;
            height: 20px;
            width: 20px;
        }

        /* --- MULTISELECT (NOTES) --- */
        .stMultiSelect label p { display: none; } /* Hide default label */
        .stMultiSelect div[data-baseweb="select"] > div {
            background-color: #1A1A1A;
            border-color: #444;
            color: white;
            border-radius: 8px;
        }
        /* Selected Tags */
        .stMultiSelect span[data-baseweb="tag"] {
            background-color: #333 !important;
            border: 1px solid #D4AF37;
        }
        .stMultiSelect span[data-baseweb="tag"] span {
            color: #D4AF37 !important;
        }

        /* --- CARD DESIGN: MODULAR SQUARES (CLEAN TEXT) --- */
        .perfume-container {
            background-color: #161616;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }

        /* Flex Layout for Name and Score */
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: stretch;
            gap: 15px;
            margin-bottom: 15px;
        }

        /* Left Box: Name */
        .box-name {
            flex: 1;
            background-color: #0A0A0A;
            border-left: 4px solid #D4AF37;
            padding: 15px;
            border-radius: 4px;
            display: flex;
            align-items: center;
        }
        .name-text {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFF;
            font-weight: 600;
            line-height: 1.2;
        }

        /* Right Box: Score */
        .box-rating {
            background-color: #D4AF37;
            color: #000;
            min-width: 65px;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 5px;
        }
        .rating-num {
            font-size: 20px;
            font-weight: 800;
        }
        .rating-lbl {
            font-size: 8px;
            font-weight: 700;
            text-transform: uppercase;
        }

        /* Notes Area */
        .notes-area {
            border-top: 1px solid #333;
            padding-top: 10px;
            margin-bottom: 15px;
        }
        .notes-label {
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .notes-text {
            font-size: 12px;
            color: #CCC;
            line-height: 1.5;
            font-style: italic;
        }

        /* Link Button */
        .fragrantica-btn {
            display: block;
            width: 100%;
            text-align: center;
            background-color: transparent;
            border: 1px solid #444;
            color: #D4AF37;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 10px 0;
            border-radius: 6px;
            text-decoration: none;
            transition: 0.2s;
        }
        .fragrantica-btn:hover {
            background-color: #D4AF37;
            color: #000;
            border-color: #D4AF37;
        }

        /* Main Title */
        .app-title {
            text-align: center;
            font-family: 'Playfair Display', serif;
            color: #D4AF37;
            font-size: 26px; /* Smaller, elegant */
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .app-subtitle {
            text-align: center;
            color: #666;
            font-size: 10px;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading & ULTRA CLEANING ---
@st.cache_data
def load_data(filepath, cache_buster_v45): 
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Fix Names
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
        
        # Map Gender
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # Get Unique Accords (Cleaned)
        all_accords = set()
        for accords_str in df['main_accords'].dropna():
            if isinstance(accords_str, str):
                # REGEX CLEANING: Keep only letters and spaces
                clean_text = re.sub(r"[^a-zA-Z, ]", "", accords_str)
                for item in clean_text.split(","):
                    item = item.strip().lower()
                    if item: all_accords.add(item)
        
        return df, sorted(list(all_accords))
    except Exception:
        return None, []

def render_card(perfume):
    """Renders the modular card."""
    
    # Clean notes for DISPLAY
    notes_display = "N/A"
    if isinstance(perfume.main_accords, str):
        # 1. Remove brackets and quotes
        clean_text = re.sub(r"[\[\]'\"]", "", perfume.main_accords)
        # 2. Split and clean individual words
        words = [w.strip().lower() for w in clean_text.split(",") if w.strip()]
        # 3. Join with stylish separator
        notes_display = " • ".join(words[:5]) # Top 5

    html = f"""
    <div class="perfume-container">
        <div class="card-header">
            <div class="box-name">
                <div class="name-text">{perfume.name}</div>
            </div>
            <div class="box-rating">
                <div class="rating-num">{perfume.score:.1f}</div>
                <div class="rating-lbl">SCORE</div>
            </div>
        </div>
        
        <div class="notes-area">
            <div class="notes-label">Key Notes</div>
            <div class="notes-text">{notes_display}</div>
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="fragrantica-btn">
            VIEW ON FRAGRANTICA
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v45="v45")

if df is not None:
    
    # --- SIDEBAR (FILTERS) ---
    with st.sidebar:
        st.markdown("<div style='text-align:center; margin-bottom:20px; color:#FFF; font-weight:bold; letter-spacing:2px;'>FILTERS</div>", unsafe_allow_html=True)
        
        # 1. GENDER (CHIPS UI)
        st.markdown('<div class="sidebar-header">1. CATEGORY</div>', unsafe_allow_html=True)
        # Using "All" as first option is standard UX
        gender = st.radio("gender_hidden", ["All", "Female", "Male", "Unisex"], horizontal=True, label_visibility="collapsed")
        
        st.write("")
        
        # 2. NOTES (Moved up as requested)
        st.markdown('<div class="sidebar-header">2. SCENT NOTES</div>', unsafe_allow_html=True)
        notes = st.multiselect("notes_hidden", unique_accords, placeholder="Select ingredients...", label_visibility="collapsed")
        
        st.write("")
        
        # 3. RATING (Bottom)
        st.markdown('<div class="sidebar-header">3. MIN RATING</div>', unsafe_allow_html=True)
        score = st.slider("score_hidden", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")

        st.markdown("<br><br><div style='color:#444; font-size:9px; text-align:center'>© 2024 Portfolio</div>", unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    st.markdown('<div class="app-title">PERFUME FINDER</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">LUXURY DATABASE</div>', unsafe_allow_html=True)

    # Logic
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_str):
            if pd.isna(row_str): return False
            # Clean logic for search
            row_clean = re.sub(r"[^a-zA-Z, ]", "", str(row_str)).lower()
            return all(note in row_clean for note in notes)
        filtered = filtered[filtered['main_accords'].apply(check_notes)]

    # Results
    st.markdown(f"<div style='color: #D4AF37; font-size: 11px; text-align: center; margin-bottom: 20px; border-bottom: 1px solid #222; padding-bottom: 10px;'>FOUND {len(filtered)} MATCHES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        # 2 Columns Grid for Desktop, Stacks on Mobile
        cols = st.columns(2)
        for i, row in enumerate(filtered.head(40).itertuples()):
            with cols[i % 2]:
                render_card(row)

else:
    st.error("Data Error")