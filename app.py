import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CSS: Compact Sidebar & Modular Cards ---
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
        [data-testid="stHeader"] { background-color: #0E0E0E; }

        /* --- SIDEBAR STYLING (COMPACT VERSION) --- */
        section[data-testid="stSidebar"] {
            background-color: #111; 
            border-right: 1px solid #333;
        }
        
        /* Sidebar Titles */
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #D4AF37 !important;
            font-family: 'Playfair Display', serif;
            margin-bottom: 10px !important; /* Less space below titles */
        }

        /* --- COMPACT RADIO BUTTONS --- */
        div[role="radiogroup"] label {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            padding: 8px 12px !important; /* Smaller padding */
            border-radius: 6px !important;
            margin-bottom: 4px !important; /* Less space between buttons */
        }
        div[role="radiogroup"] label p {
            font-size: 13px !important; /* Slightly smaller text */
        }
        
        /* Selected State (Gold) */
        div[role="radiogroup"] label:has(input:checked) {
            background-color: #D4AF37 !important;
            border-color: #D4AF37 !important;
        }
        div[role="radiogroup"] label:has(input:checked) p {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        div[role="radiogroup"] label div[data-baseweb="radio"] { display: none; }

        /* --- COMPACT SLIDER --- */
        div[data-testid="stSlider"] {
            padding-top: 0px !important;
            padding-bottom: 10px !important;
        }
        div[data-testid="stSlider"] label p { color: #FFF !important; font-size: 13px; }
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p { color: #D4AF37 !important; font-weight:700; }
        div[data-testid="stSlider"] .st-ae { background-color: #D4AF37 !important; }

        /* --- CARD DESIGN: SEPARATE SQUARES --- */
        .perfume-container {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #222;
        }

        /* The Flex Row for Name Box and Rating Box */
        .info-row {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            align-items: stretch; /* Make them equal height */
        }

        /* Square 1: Name */
        .box-name {
            flex-grow: 1; /* Takes remaining space */
            background-color: #161616;
            border: 1px solid #333;
            border-left: 3px solid #D4AF37;
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

        /* Square 2: Rating */
        .box-rating {
            background-color: #D4AF37; /* Gold Background */
            color: #000;
            min-width: 70px; /* Fixed width square */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 4px;
            padding: 5px;
        }
        .rating-num {
            font-size: 18px;
            font-weight: 800;
        }
        .rating-sub {
            font-size: 9px;
            font-weight: 600;
            text-transform: uppercase;
        }

        /* Notes section */
        .notes-row {
            font-size: 11px;
            color: #888;
            margin-bottom: 10px;
            padding-left: 5px;
        }
        .note-highlight {
            color: #CCC;
            font-style: italic;
        }

        /* Link Button */
        .fragrantica-link {
            display: block;
            text-align: right;
            font-size: 10px;
            color: #D4AF37;
            text-decoration: none;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .fragrantica-link:hover {
            text-decoration: underline;
        }
        
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v29): # v29 Cache Buster
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Fix names
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

def render_modular_card(perfume):
    """Renders separate boxes for Name and Rating."""
    
    notes_str = "N/A"
    if isinstance(perfume.main_accords, str):
        # Clean the raw string like "['citrus', 'woody']"
        raw = perfume.main_accords.strip("[]").replace("'", "").replace('"', '').split(",")
        clean = [n.strip().lower() for n in raw if n.strip()]
        notes_str = ", ".join(clean[:5]) # Take top 5

    html = f"""
    <div class="perfume-container">
        <div class="info-row">
            <div class="box-name">
                <div class="name-text">{perfume.name}</div>
            </div>
            <div class="box-rating">
                <div class="rating-num">{perfume.score:.1f}</div>
                <div class="rating-sub">SCORE</div>
            </div>
        </div>
        
        <div class="notes-row">
            NOTES: <span class="note-highlight">{notes_str}</span>
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="fragrantica-link">
            VIEW ON FRAGRANTICA ↗
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v29="v29")

if df is not None:
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("### FILTER SEARCH")
        
        # Gender
        st.write("")
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        # Score
        st.markdown("---")
        st.markdown("**MIN RATING**")
        score = st.slider("MIN RATING", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        # Notes
        st.markdown("---")
        notes = st.multiselect("SCENT NOTES", unique_accords, placeholder="Type ingredient...")
        
        st.markdown("<br><br><div style='color:#444; font-size:10px'>© 2024 Portfolio</div>", unsafe_allow_html=True)

    # --- MAIN AREA ---
    st.markdown("<h1 style='text-align: center; font-family: Playfair Display; color: #D4AF37; margin-bottom: 0;'>PERFUME FINDER</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #666; font-size: 11px; margin-bottom: 30px; letter-spacing: 2px;'>LUXURY DATABASE</div>", unsafe_allow_html=True)

    # Filtering
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_str):
            if pd.isna(row_str): return False
            # Stronger cleaning for logic
            row_clean = row_str.strip("[]").replace("'", "").replace('"', "").lower()
            return all(note in row_clean for note in notes)
        filtered = filtered[filtered['main_accords'].apply(check_notes)]

    # Results
    st.markdown(f"<div style='color: #888; font-size: 12px; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 5px;'>FOUND {len(filtered)} MATCHES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        for row in filtered.head(50).itertuples():
            render_modular_card(row)

else:
    st.error("Data Error.")