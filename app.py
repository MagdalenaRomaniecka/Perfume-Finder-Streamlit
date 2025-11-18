import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CSS: Modern, Clean, No "Keyboard" Glitch ---
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
        
        /* --- CRITICAL: REMOVE TOP HEADER & KEYBOARD GLITCH --- */
        header { visibility: hidden; }
        [data-testid="stHeader"] { display: none; }
        .block-container { padding-top: 2rem !important; }

        /* --- SIDEBAR STYLING --- */
        section[data-testid="stSidebar"] {
            background-color: #121212; 
            border-right: 1px solid #333;
        }
        /* Cleaner Sidebar Inputs */
        .stSidebar label p {
            color: #D4AF37 !important; 
            font-size: 11px !important;
            letter-spacing: 1px;
            font-weight: 700;
        }

        /* --- MODERN CARD DESIGN (The "Squares" Look) --- */
        .perfume-card {
            background-color: #1A1A1A;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s;
        }
        .perfume-card:hover {
            border-color: #D4AF37;
            transform: translateY(-2px);
        }

        /* Top Row: Name and Rating Box */
        .card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 12px;
        }

        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 16px;
            color: #FFF;
            font-weight: 600;
            line-height: 1.2; /* Tighter line height fixes "rozjechanie" */
        }

        .rating-badge {
            background-color: #D4AF37;
            color: #000;
            font-size: 12px;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 4px;
            white-space: nowrap;
            min-width: 45px;
            text-align: center;
        }

        /* Middle: Notes as Tags/Pills */
        .notes-container {
            margin-bottom: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }
        
        .note-tag {
            background-color: #252525;
            color: #AAA;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            border: 1px solid #333;
            text-transform: lowercase;
        }

        /* Bottom: Link Button */
        .link-btn {
            display: block;
            width: 100%;
            text-align: center;
            background-color: transparent;
            border: 1px solid #D4AF37;
            color: #D4AF37;
            text-decoration: none;
            font-size: 10px;
            font-weight: 700;
            padding: 8px 0;
            border-radius: 4px;
            transition: all 0.2s;
            letter-spacing: 1px;
        }
        .link-btn:hover {
            background-color: #D4AF37;
            color: #000;
        }

        /* --- WIDGET CONTRAST FIXES --- */
        div[role="radiogroup"] label p { color: #FFF !important; }
        div[data-testid="stSlider"] p { color: #FFF !important; }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v31): 
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
                # Clean: ['citrus', 'woody'] -> list
                raw_list = accords_str.replace("[", "").replace("]", "").replace("'", "").replace('"', "").split(",")
                for item in raw_list:
                    clean_item = item.strip().lower()
                    if clean_item: all_accords.add(clean_item)
        
        return df, sorted(list(all_accords))
    except Exception:
        return None, []

def render_modern_card(perfume):
    """Renders a modern card with tags and a button."""
    
    # Create HTML tags for notes
    tags_html = ""
    if isinstance(perfume.main_accords, str):
        raw = perfume.main_accords.replace("[", "").replace("]", "").replace("'", "").replace('"', "").split(",")
        clean = [n.strip().lower() for n in raw[:4] if n.strip()] # Top 4 notes
        for note in clean:
            tags_html += f'<span class="note-tag">{note}</span>'

    html = f"""
    <div class="perfume-card">
        <div class="card-top">
            <div class="p-name">{perfume.name}</div>
            <div class="rating-badge">{perfume.score:.1f}</div>
        </div>
        
        <div class="notes-container">
            {tags_html}
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="link-btn">
            VIEW ON FRAGRANTICA ↗
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v31="v31")

if df is not None:
    
    # --- SIDEBAR FILTERS ---
    with st.sidebar:
        st.markdown("<h3 style='color:#D4AF37; font-family:Playfair Display; margin-top:0;'>FILTER SEARCH</h3>", unsafe_allow_html=True)
        
        st.write("")
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], index=0)
        
        st.markdown("---")
        st.markdown("**MIN RATING**")
        score = st.slider("rating_slider", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.markdown("---")
        notes = st.multiselect("SCENT NOTES", unique_accords, placeholder="Type ingredients...")
        
        st.markdown("<br><br><div style='color:#444; font-size:9px'>© 2024 Portfolio</div>", unsafe_allow_html=True)

    # --- MAIN AREA ---
    st.markdown("<h1 style='text-align: center; font-family: Playfair Display; color: #D4AF37; margin-bottom: 0; font-size: 32px;'>PERFUME FINDER</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #666; font-size: 10px; margin-bottom: 25px; letter-spacing: 2px;'>LUXURY DATABASE</div>", unsafe_allow_html=True)

    # Filtering
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

    # Results Info
    st.markdown(f"<div style='color: #888; font-size: 11px; margin-bottom: 10px; border-bottom: 1px solid #222; padding-bottom:5px;'>FOUND {len(filtered)} MATCHES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        # Grid Layout: 2 columns on desktop, auto-stack on mobile
        cols = st.columns(2)
        for i, row in enumerate(filtered.head(40).itertuples()):
            with cols[i % 2]:
                render_modern_card(row)

else:
    st.error("Data Error.")