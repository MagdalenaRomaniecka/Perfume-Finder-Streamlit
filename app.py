import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS: Mobile-First, High Contrast & Framed Headers ---
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
        [data-testid="stHeader"] { background-color: #050505; }

        /* HIDE SIDEBAR ELEMENTS */
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none; }

        /* --- AESTHETIC FRAMED HEADER --- */
        .luxury-frame {
            border: 2px solid #D4AF37; /* Gold Border */
            padding: 30px;
            border-radius: 0px; /* Sharp, elegant corners */
            text-align: center;
            margin-bottom: 30px;
            background-color: #111;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.1); /* Subtle gold glow */
        }
        
        .luxury-title {
            font-family: 'Playfair Display', serif;
            font-size: 42px !important; /* Much larger title */
            color: #D4AF37; /* Gold */
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .luxury-subtitle {
            font-family: 'Montserrat', sans-serif;
            font-size: 14px;
            color: #FFFFFF;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 10px;
        }

        /* --- VISIBILITY FIXES FOR INPUTS (CRITICAL) --- */
        
        /* 1. Radio Buttons (Gender) */
        div[role="radiogroup"] label {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            padding: 10px 15px !important;
            border-radius: 5px !important;
            margin-right: 10px !important;
            transition: all 0.3s ease;
        }
        /* Force text color inside radio buttons to be WHITE */
        div[role="radiogroup"] label p {
            color: #FFFFFF !important; 
            font-weight: 600 !important;
            font-size: 16px !important;
        }
        /* Hover effect */
        div[role="radiogroup"] label:hover {
            border-color: #D4AF37 !important;
        }

        /* 2. Slider (Rating) */
        /* The label above the slider */
        div[data-testid="stSlider"] label p {
            color: #D4AF37 !important; /* Gold Label */
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        /* The numbers on the slider */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
        }

        /* 3. Multiselect (Notes) */
        .stMultiSelect label p {
            color: #D4AF37 !important; /* Gold Label */
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        /* The selected items (tags) */
        .stMultiSelect span[data-baseweb="tag"] {
            background-color: #D4AF37 !important;
            color: black !important;
        }
        
        /* --- PERFUME CARD STYLING --- */
        .perfume-card {
            background-color: #121212;
            border: 1px solid #333;
            border-left: 5px solid #D4AF37; /* Thicker gold accent */
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        }
        
        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 22px; /* Larger Name */
            color: #FFFFFF;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .p-rating {
            font-size: 14px;
            color: #D4AF37; 
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .p-notes {
            font-size: 12px;
            color: #AAAAAA;
            font-style: italic;
            margin-top: 8px;
            line-height: 1.5;
        }

        .p-link {
            display: inline-block;
            margin-top: 15px;
            font-size: 11px;
            color: #000;
            background-color: #D4AF37; /* Gold Button */
            padding: 8px 16px;
            text-decoration: none;
            font-weight: 700;
            letter-spacing: 1px;
            border-radius: 2px;
        }
        
        /* Expander Styling */
        .streamlit-expanderHeader {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFFFFF !important;
            background-color: #1A1A1A !important;
            border: 1px solid #D4AF37 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v16): # v16 Cache Buster
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
        <a href="{perfume.img_link}" target="_blank" class="p-link">VIEW DETAILS</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v16="v16")

if df is not None:
    
    # --- FRAMED HEADER ---
    st.markdown("""
        <div class="luxury-frame">
            <h1 class="luxury-title">Perfume Finder</h1>
            <div class="luxury-subtitle">Exclusive Fragrance Database</div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- FILTERS ---
    with st.expander("▼  FILTER SEARCH  ▼", expanded=True):
        
        st.write("")
        # Gender (Radio)
        gender = st.radio("SELECT GENDER", ["Female", "Male", "Unisex"], horizontal=True)
        
        st.write("")
        st.markdown("<hr style='border-color: #333; margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Score (Slider)
        score = st.slider("MINIMUM RATING", 1.0, 5.0, 4.0, 0.1)
        
        st.write("")
        st.markdown("<hr style='border-color: #333; margin: 10px 0;'>", unsafe_allow_html=True)

        # Notes (Multiselect)
        notes = st.multiselect("SCENT NOTES", unique_accords, placeholder="Search ingredients...")
        
    # --- FILTERING LOGIC ---
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
    st.markdown(f"<div style='text-align: center; color: #D4AF37; letter-spacing: 2px; margin-bottom: 20px; font-size: 14px;'>FOUND {len(filtered)} MATCHES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found. Try adjusting your filters.")
    else:
        for row in filtered.head(50).itertuples():
            render_luxury_card(row)
            
    st.markdown("<br><br><div style='text-align: center; color: #444; font-size: 10px;'>© 2024 Portfolio Project</div>", unsafe_allow_html=True)

else:
    st.error("System Error: Data could not be loaded.")