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

# --- CSS: Vine Background, Glassmorphism & Consistent Typography ---
def load_custom_css():
    # URL to a dark luxury vine/floral pattern
    bg_image_url = "https://img.freepik.com/free-vector/dark-floral-background-with-gold-leaves_1017-30553.jpg?t=st=1716385000~exp=1716388600~hmac=e5b2c8" 
    # Fallback to dark if image breaks, but image adds the vibe.

    st.markdown(f"""
        <style>
        /* Import Elegant Fonts: Playfair Display (Headers) & Lato (Body) */
        @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&family=Playfair+Display:wght@400;600;700&display=swap');

        /* --- GLOBAL RESET & TYPOGRAPHY --- */
        html, body, [class*="st-"], [class*="css-"] {{
            font-family: 'Lato', sans-serif !important; /* Base font for everything */
            color: #E0E0E0 !important;
        }}
        
        /* Headings Force Playfair */
        h1, h2, h3, .p-name {{
            font-family: 'Playfair Display', serif !important;
        }}

        /* --- BACKGROUND WITH VINES --- */
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), url("https://img.freepik.com/free-vector/elegant-dark-green-background-with-golden-leaves_1017-30554.jpg");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        [data-testid="stHeader"] {{ background: transparent !important; }}

        /* --- SIDEBAR (GLASS EFFECT) --- */
        section[data-testid="stSidebar"] {{
            background-color: rgba(10, 10, 10, 0.9) !important; /* Dark semi-transparent */
            border-right: 1px solid #333;
            backdrop-filter: blur(5px);
        }}
        
        /* Sidebar Titles */
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {{
            color: #D4AF37 !important;
            font-weight: 400 !important;
            letter-spacing: 1px;
            font-size: 16px !important;
            text-transform: uppercase;
            margin-top: 20px !important;
        }}

        /* --- UNIFIED INPUT STYLING --- */
        /* Labels */
        .stSidebar label p {{
            font-size: 11px !important;
            color: #AAA !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        /* Radio Buttons */
        div[role="radiogroup"] label {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
            padding: 8px 12px !important;
        }}
        div[role="radiogroup"] label p {{
            font-size: 13px !important;
            color: #CCC !important;
        }}
        /* Selected Radio */
        div[role="radiogroup"] label:has(input:checked) {{
            background-color: #D4AF37 !important;
            border-color: #D4AF37 !important;
        }}
        div[role="radiogroup"] label:has(input:checked) p {{
            color: #000 !important;
            font-weight: 700 !important;
        }}
        div[role="radiogroup"] label div[data-baseweb="radio"] {{ display: none; }}

        /* Slider */
        div[data-testid="stSlider"] label p {{ color: #D4AF37 !important; }}
        div[data-testid="stSlider"] .st-ae {{ background-color: #D4AF37 !important; }}

        /* --- CARD DESIGN (GLASS & GOLD) --- */
        .perfume-container {{
            background-color: rgba(20, 20, 20, 0.8); /* Glass effect */
            border: 1px solid #333;
            border-top: 3px solid #D4AF37; /* Top gold bar */
            border-radius: 0px; /* Sharp elegant corners */
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }}

        .info-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}

        /* Name Section */
        .box-name {{
            flex-grow: 1;
        }}
        .name-text {{
            font-size: 18px;
            color: #FFF;
            font-weight: 400;
            letter-spacing: 0.5px;
            line-height: 1.2;
        }}
        .brand-text {{
             font-size: 10px;
             color: #888;
             text-transform: uppercase;
             letter-spacing: 1px;
             margin-top: 4px;
        }}

        /* Rating Box */
        .box-rating {{
            background-color: transparent;
            border: 1px solid #D4AF37;
            color: #D4AF37;
            min-width: 60px;
            text-align: center;
            padding: 5px;
            border-radius: 0px;
        }}
        .rating-num {{
            font-size: 16px;
            font-weight: 700;
            font-family: 'Lato', sans-serif;
        }}
        .rating-sub {{
            font-size: 8px;
            text-transform: uppercase;
        }}

        /* Notes */
        .notes-row {{
            font-size: 11px;
            color: #AAA;
            margin-bottom: 15px;
            line-height: 1.6;
            font-style: italic;
            font-family: 'Playfair Display', serif; /* Elegant font for notes */
        }}

        /* Button */
        .fragrantica-link {{
            display: block;
            text-align: center;
            font-size: 10px;
            color: #000;
            background-color: #D4AF37;
            text-decoration: none;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 10px 0;
            border-radius: 0px;
            transition: 0.3s;
        }}
        .fragrantica-link:hover {{
            background-color: #FFF;
            color: #000;
        }}
        
        /* Main Title Style */
        .main-title {{
            font-size: 40px;
            color: #D4AF37;
            text-align: center;
            font-weight: 400;
            letter-spacing: 2px;
            margin-bottom: 5px;
        }}
        .sub-title {{
            font-family: 'Lato', sans-serif;
            font-size: 10px;
            color: #AAA;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin-bottom: 40px;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v38): 
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
                # Advanced clean
                clean_str = re.sub(r"[\[\]'\"]", "", accords_str)
                raw_list = clean_str.split(",")
                for item in raw_list:
                    clean_item = item.strip().lower()
                    if clean_item: all_accords.add(clean_item)
        
        return df, sorted(list(all_accords))
    except Exception:
        return None, []

def render_luxury_card(perfume):
    """Renders the final luxury card."""
    
    notes_str = "Notes unavailable"
    if isinstance(perfume.main_accords, str):
        # Clean raw string
        clean_str = re.sub(r"[\[\]'\"]", "", perfume.main_accords)
        clean = [n.strip().lower() for n in clean_str.split(",") if n.strip()]
        notes_str = ", ".join(clean[:5])

    html = f"""
    <div class="perfume-container">
        <div class="info-row">
            <div class="box-name">
                <div class="name-text">{perfume.name}</div>
                <div class="brand-text">EAU DE PARFUM</div>
            </div>
            <div class="box-rating">
                <div class="rating-num">{perfume.score:.1f}</div>
                <div class="rating-sub">SCORE</div>
            </div>
        </div>
        
        <div class="notes-row">
            {notes_str}
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="fragrantica-link">
            DISCOVER
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v38="v38")

if df is not None:
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("### FILTER COLLECTION")
        
        st.write("")
        gender = st.radio("CATEGORY", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        st.write("")
        st.markdown("**MINIMUM RATING**")
        score = st.slider("min_rating", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.write("")
        st.markdown("**OLFACTORY NOTES**")
        notes = st.multiselect("scent_notes", unique_accords, placeholder="Select ingredients...", label_visibility="collapsed")
        
        st.markdown("<br><br><br><div style='color:#666; font-size:9px; letter-spacing:1px; text-align:center'>DESIGNED BY<br>MAGDALENA ROMANIECKA</div>", unsafe_allow_html=True)

    # --- MAIN AREA ---
    st.markdown('<div class="main-title">PERFUME FINDER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">EXCLUSIVE FRAGRANCE DATABASE</div>', unsafe_allow_html=True)

    # Filtering
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_str):
            if pd.isna(row_str): return False
            row_clean = re.sub(r"[\[\]'\"]", "", row_str).lower()
            return all(note in row_clean for note in notes)
        filtered = filtered[filtered['main_accords'].apply(check_notes)]

    # Results
    st.markdown(f"<div style='color: #D4AF37; font-size: 10px; letter-spacing: 2px; margin-bottom: 20px; text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px;'>{len(filtered)} FRAGRANCES FOUND</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found matching your criteria.")
    else:
        # Grid Layout (2 columns)
        cols = st.columns(2)
        for i, row in enumerate(filtered.head(40).itertuples()):
            with cols[i % 2]:
                render_luxury_card(row)

else:
    st.error("System Error: Data could not be loaded.")