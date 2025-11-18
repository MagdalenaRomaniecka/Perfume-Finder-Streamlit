import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded" # Sidebar always open on desktop
)

# --- CSS: High Contrast, Sidebar Styling, Boxed Layout ---
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

        /* --- SIDEBAR STYLING --- */
        section[data-testid="stSidebar"] {
            background-color: #121212; /* Slightly lighter than main bg */
            border-right: 1px solid #333;
        }
        /* Sidebar Titles */
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #D4AF37 !important;
            font-family: 'Playfair Display', serif;
        }

        /* --- 1. GENDER RADIO BUTTONS (HIGHLIGHT EFFECT) --- */
        /* Default State */
        div[role="radiogroup"] label {
            background-color: #1E1E1E !important;
            border: 1px solid #333 !important;
            padding: 12px !important;
            border-radius: 8px !important;
            margin-bottom: 8px !important;
            transition: all 0.3s ease;
        }
        div[role="radiogroup"] label p {
            color: #888 !important;
            font-weight: 500 !important;
            font-size: 14px !important;
        }
        
        /* ACTIVE/SELECTED STATE (The "Highlight") */
        /* When checked, turn background GOLD and text BLACK */
        div[role="radiogroup"] label:has(input:checked) {
            background-color: #D4AF37 !important;
            border-color: #D4AF37 !important;
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.4);
        }
        div[role="radiogroup"] label:has(input:checked) p {
            color: #000000 !important; /* Black text for contrast */
            font-weight: 700 !important;
        }
        /* Hide the little circle to make it look like a button */
        div[role="radiogroup"] label div[data-baseweb="radio"] {
            display: none; 
        }

        /* --- 2. SLIDER VISIBILITY --- */
        /* Labels (Min Rating) */
        div[data-testid="stSlider"] label p {
            color: #FFFFFF !important;
            font-size: 14px !important;
        }
        /* The Numbers (1.0, 5.0) */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
            color: #D4AF37 !important; /* Gold numbers */
            font-size: 16px !important;
            font-weight: 700 !important;
        }
        /* The Track */
        div[data-testid="stSlider"] div[data-baseweb="slider"] div {
            background-color: #444 !important;
        }
        /* The Filled Track */
        div[data-testid="stSlider"] .st-ae {
            background-color: #D4AF37 !important;
        }

        /* --- 3. PERFUME CARD (BOXED LAYOUT) --- */
        .perfume-card {
            background-color: #181818;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            position: relative;
        }

        /* The "Squares" Container */
        .card-header {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            align-items: stretch;
        }

        /* Name Box */
        .name-box {
            flex-grow: 1;
            background-color: #0E0E0E;
            border: 1px solid #D4AF37;
            padding: 12px;
            border-radius: 4px;
            display: flex;
            align-items: center;
        }
        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFFFFF;
            font-weight: 700;
            margin: 0;
            line-height: 1.1;
        }

        /* Rating Box */
        .rating-box {
            background-color: #D4AF37;
            color: #000;
            padding: 10px;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-width: 60px;
        }
        .rating-val {
            font-size: 18px;
            font-weight: 800;
        }
        .rating-label {
            font-size: 9px;
            text-transform: uppercase;
            font-weight: 600;
        }

        /* Notes */
        .p-notes {
            font-size: 12px;
            color: #AAA;
            margin-bottom: 15px;
            line-height: 1.5;
            border-left: 2px solid #333;
            padding-left: 10px;
        }

        /* Fragrantica Button */
        .fragrantica-btn {
            display: block;
            width: 100%;
            text-align: center;
            background-color: #252525;
            color: #FFF;
            border: 1px solid #444;
            padding: 10px 0;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            border-radius: 6px;
            transition: 0.3s;
        }
        .fragrantica-btn:hover {
            background-color: #D4AF37;
            color: #000;
            border-color: #D4AF37;
        }

        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v28): 
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Fix names
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
        # Map Gender
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # Cleanup
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

def render_boxed_card(perfume):
    """Renders a card with 'boxed' layout (Name box + Rating box)."""
    
    notes_str = "No notes data"
    if isinstance(perfume.main_accords, str):
        raw = perfume.main_accords.strip("[]").split(",")
        clean = [n.strip().strip("'\"").strip().lower() for n in raw[:5]]
        notes_str = ", ".join(clean)

    html = f"""
    <div class="perfume-card">
        <div class="card-header">
            <div class="name-box">
                <div class="p-name">{perfume.name}</div>
            </div>
            <div class="rating-box">
                <div class="rating-val">{perfume.score:.1f}</div>
                <div class="rating-label">SCORE</div>
            </div>
        </div>
        
        <div class="p-notes">
            <span style="color: #D4AF37;">NOTES:</span> {notes_str}
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="fragrantica-btn">
            VIEW ON FRAGRANTICA ↗
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v28="v28")

if df is not None:
    
    # --- SIDEBAR FILTERS (ALWAYS VISIBLE ON DESKTOP) ---
    with st.sidebar:
        st.markdown("### 🔎 FILTER PERFUMES")
        st.write("")
        
        # 1. GENDER (Now highlights Gold!)
        st.markdown("**GENDER CATEGORY**")
        gender = st.radio("Hidden_Gender", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        st.write("")
        st.markdown("---")
        st.write("")

        # 2. RATING (Numbers are bigger and gold)
        score = st.slider("MINIMUM RATING", 1.0, 5.0, 4.0, 0.1)
        
        st.write("")
        st.markdown("---")
        st.write("")

        # 3. NOTES
        notes = st.multiselect("SCENT NOTES", unique_accords, placeholder="Choose ingredients...")
        
        st.markdown("<br><br><div style='color:#555; font-size:10px'>© 2024 Luxury Database</div>", unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    st.markdown("<h1 style='text-align: center; font-family: Playfair Display; color: #D4AF37; letter-spacing: 2px;'>PERFUME FINDER</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #666; font-size: 11px; margin-bottom: 30px;'>DISCOVER YOUR SIGNATURE SCENT</div>", unsafe_allow_html=True)

    # --- LOGIC ---
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
    st.markdown(f"<div style='border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px; color: #888;'>FOUND {len(filtered)} RESULTS</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        # Limit to 50
        for row in filtered.head(50).itertuples():
            render_boxed_card(row)

else:
    st.error("Error loading data.")