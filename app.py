import streamlit as st
import pandas as pd
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CSS: Luxury Grid, Dark Sidebar, Typography ---
def load_custom_css():
    # Background pattern URL (Subtle Black Linen)
    bg_url = "https://www.transparenttextures.com/patterns/black-linen.png"
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        /* --- Global Settings --- */
        html, body, [class*="st-"], [class*="css-"] {{
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #0a0a0a;
            background-image: url("{bg_url}");
        }}
        [data-testid="stAppViewContainer"] {{
            background-color: rgba(10, 10, 10, 0.95);
        }}
        
        /* Hide default header decorations */
        header {{ visibility: hidden; }}
        .block-container {{ padding-top: 2rem !important; }}

        /* --- Sidebar Styling --- */
        section[data-testid="stSidebar"] {{
            background-color: #111;
            border-right: 1px solid #333;
        }}
        
        /* Sidebar Headers */
        .sidebar-header {{
            color: #D4AF37;
            font-family: 'Playfair Display', serif;
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }}

        /* --- Input Widgets Styling --- */
        
        /* Radio Buttons */
        div[role="radiogroup"] label {{
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            padding: 10px !important;
            border-radius: 4px !important;
            margin-bottom: 5px !important;
            transition: all 0.3s;
        }}
        div[role="radiogroup"] label p {{
            font-size: 13px !important;
            color: #888 !important;
            font-weight: 500 !important;
        }}
        
        /* Active State for Radio Buttons */
        div[role="radiogroup"] label:has(input:checked) {{
            border: 1px solid #D4AF37 !important;
            background-color: #222 !important;
        }}
        div[role="radiogroup"] label:has(input:checked) p {{
            color: #D4AF37 !important;
            font-weight: 700 !important;
        }}
        div[role="radiogroup"] label div[data-baseweb="radio"] {{ display: none; }}

        /* Sliders and Dropdowns */
        div[data-testid="stSlider"] p {{ color: #D4AF37 !important; font-weight: 600; }}
        .stMultiSelect span {{ color: #FFF; }}
        
        /* --- Perfume Card Layout --- */
        .perfume-row {{
            background-color: #161616;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }}
        .perfume-row:hover {{
            border-color: #D4AF37;
            transform: translateY(-2px);
        }}

        /* Top Section: Logo + Name + Rating */
        .card-top {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        /* Monogram Box */
        .box-logo {{
            width: 50px;
            height: 50px;
            min-width: 50px;
            background: linear-gradient(135deg, #D4AF37, #B49018);
            color: #000;
            font-family: 'Playfair Display', serif;
            font-size: 24px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
        }}

        /* Name Section */
        .box-name {{
            flex-grow: 1;
        }}
        .name-text {{
            font-family: 'Playfair Display', serif;
            font-size: 17px;
            color: #FFF;
            font-weight: 600;
            line-height: 1.1;
        }}
        .brand-text {{
            font-size: 10px;
            color: #888;
            text-transform: uppercase;
            margin-top: 3px;
        }}

        /* Rating Box */
        .box-rating {{
            border: 1px solid #D4AF37;
            color: #D4AF37;
            padding: 5px 10px;
            border-radius: 6px;
            text-align: center;
            min-width: 55px;
        }}
        .rating-val {{ font-size: 14px; font-weight: 800; }}
        .rating-lbl {{ font-size: 8px; text-transform: uppercase; }}

        /* Notes Section */
        .notes-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 5px;
            padding-top: 10px;
            border-top: 1px solid #222;
        }}
        .note-tag {{
            background-color: #252525;
            color: #BBB;
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 10px;
            border: 1px solid #333;
        }}

        /* Link Button */
        .link-btn {{
            display: block;
            margin-top: 10px;
            text-align: center;
            color: #D4AF37;
            font-size: 10px;
            text-decoration: none;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 8px;
            border: 1px solid #333;
            border-radius: 4px;
            transition: 0.2s;
        }}
        .link-btn:hover {{
            background-color: #D4AF37;
            color: #000;
        }}

        /* Main Header */
        .main-header {{
            text-align: center;
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            color: #D4AF37;
            margin-bottom: 5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }}
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading & Cleaning ---
@st.cache_data
def load_data(filepath, version_hash):
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # 1. Clean glued names (e.g. "Namefor women" -> "Name")
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
            
        # 2. Map Gender categories
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # 3. Remove incomplete rows
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # 4. Ensure numeric score
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # 5. Extract unique accords with strict regex cleaning
        all_accords = set()
        for accords_str in df['main_accords'].dropna():
            # Remove all non-alphanumeric characters except commas and spaces
            clean_str = re.sub(r"[^a-zA-Z, ]", "", str(accords_str))
            for item in clean_str.split(","):
                item = item.strip().lower()
                if item: all_accords.add(item)
        
        return df, sorted(list(all_accords))
    except Exception:
        return None, []

def render_modular_card(perfume):
    """Renders the perfume card with modular layout."""
    
    # Initial letter for the logo box
    initial = perfume.name[0].upper() if perfume.name else "P"
    
    # Clean notes for display
    notes_html = ""
    if isinstance(perfume.main_accords, str):
        # Strict regex cleaning to remove brackets/quotes artifacts
        clean_str = re.sub(r"[^a-zA-Z, ]", "", str(perfume.main_accords))
        notes = [n.strip().lower() for n in clean_str.split(",") if n.strip()][:4] # Show top 4 notes
        for n in notes:
            notes_html += f'<span class="note-tag">{n}</span>'

    html = f"""
    <div class="perfume-row">
        <div class="card-top">
            <div class="box-logo">{initial}</div>
            <div class="box-name">
                <div class="name-text">{perfume.name}</div>
                <div class="brand-text">EAU DE PARFUM</div>
            </div>
            <div class="box-rating">
                <div class="rating-val">{perfume.score:.1f}</div>
                <div class="rating-lbl">SCORE</div>
            </div>
        </div>
        
        <div class="notes-container">
            {notes_html}
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="link-btn">VIEW ON FRAGRANTICA</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Logic ---

# Load CSS and Data
load_custom_css()
# Version hash forces cache refresh on deployment
df, unique_accords = load_data("fra_perfumes.csv", version_hash="v1.0_FINAL") 

if df is not None:
    
    # --- Sidebar Filters ---
    with st.sidebar:
        st.markdown("<div style='text-align:center; color:#FFF; font-weight:bold; letter-spacing:2px; margin-bottom:20px;'>FILTERS</div>", unsafe_allow_html=True)
        
        # Gender
        st.markdown('<div class="sidebar-header">1. Category</div>', unsafe_allow_html=True)
        gender = st.radio("gender_select", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        # Rating
        st.markdown('<div class="sidebar-header">2. Rating</div>', unsafe_allow_html=True)
        score = st.slider("min_score", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        # Notes
        st.markdown('<div class="sidebar-header">3. Composition</div>', unsafe_allow_html=True)
        notes = st.multiselect("notes_select", unique_accords, placeholder="Select notes...", label_visibility="collapsed")
        
        st.markdown("<br><br><div style='color:#444; font-size:10px; text-align:center'>© 2024 Portfolio Project</div>", unsafe_allow_html=True)

    # --- Main Area ---
    st.markdown('<div class="main-header">PERFUME FINDER</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #777; font-size: 11px; margin-bottom: 30px; letter-spacing: 2px;">LUXURY FRAGRANCE DATABASE</div>', unsafe_allow_html=True)

    # --- Filtering Engine ---
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_str):
            if pd.isna(row_str): return False
            # Clean comparison
            row_clean = re.sub(r"[^a-zA-Z, ]", "", str(row_str)).lower()
            return all(note in row_clean for note in notes)
        filtered = filtered[filtered['main_accords'].apply(check_notes)]

    # --- Results Grid ---
    st.markdown(f"<div style='color: #D4AF37; font-size: 12px; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 5px;'>FOUND {len(filtered)} MATCHES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found matching these criteria.")
    else:
        # Responsive Grid: 2 columns on desktop, stacks on mobile
        cols = st.columns(2)
        for i, row in enumerate(filtered.head(40).itertuples()):
            with cols[i % 2]:
                render_modular_card(row)

else:
    st.error("Data Error: Unable to load dataset.")