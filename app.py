import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS for Mobile-First Design (No Sidebar, No Images, Clean Luxury Look) ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        /* Dark App Background - Deep Black */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #0E0E0E; 
        }
        [data-testid="stAppViewContainer"] { background-color: #0E0E0E; }
        [data-testid="stHeader"] { background-color: #0E0E0E; }

        /* HIDE SIDEBAR (Fixes the issue of overlapping top bar on mobile) */
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none; }

        /* --- PERFUME CARD STYLING (Text-Only Luxury Card) --- */
        /* Looks like a luxury business card */
        .perfume-card {
            background-color: #1A1A1A;
            border-left: 4px solid #D4AF37; /* Gold accent instead of image */
            border-radius: 0 8px 8px 0;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        
        .perfume-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 8px;
        }

        .p-name {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFFFFF;
            font-weight: 700;
            line-height: 1.2;
            margin: 0;
            flex-grow: 1;
        }

        .p-rating {
            font-size: 13px;
            color: #0E0E0E; 
            background-color: #D4AF37; /* Gold background for rating */
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            margin-left: 10px;
            white-space: nowrap;
        }

        .p-notes {
            font-size: 11px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 6px;
            line-height: 1.4;
        }

        .p-link {
            display: block;
            margin-top: 12px;
            font-size: 11px;
            color: #D4AF37;
            text-decoration: none;
            text-align: right;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        /* --- FILTER STYLING (EXPANDER) --- */
        /* Filter panel on main page */
        .streamlit-expanderHeader {
            background-color: #1A1A1A !important;
            color: #D4AF37 !important;
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
            border: 1px solid #333;
            border-radius: 8px;
        }
        
        /* Fix input visibility */
        .stMultiSelect div[data-baseweb="select"] > div {
            background-color: #252525;
            border-color: #444;
            color: white;
        }
        
        /* Dropdown list text color */
        div[role="listbox"] ul li {
            color: white !important;
            background-color: #252525 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(filepath, cache_buster_v14): # v14 Cache Buster
    try:
        df = pd.read_csv(filepath)
        # Rename columns to internal names
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # 1. FIX GLUED NAMES (e.g. "9am Afnanfor women" -> "9am Afnan")
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
            
        # 2. MAP GENDER (Fix zero results issue)
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # Clean empty rows
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # Convert score to float
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # 3. CLEAN ACCORDS (Fix duplicate 'aldehydic' issue)
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

def render_clean_card(perfume):
    """Renders a clean HTML card without images, focusing on elegant typography."""
    
    # Prepare notes string
    notes_str = ""
    if isinstance(perfume.main_accords, str):
        raw = perfume.main_accords.strip("[]").split(",")
        clean = [n.strip().strip("'\"").strip().lower() for n in raw[:5]] # Show top 5 notes
        notes_str = " • ".join(clean)

    html = f"""
    <a href="{perfume.img_link}" target="_blank" style="text-decoration: none;">
        <div class="perfume-card">
            <div class="perfume-header">
                <div class="p-name">{perfume.name}</div>
                <div class="p-rating">★ {perfume.score:.2f}</div>
            </div>
            <div class="p-notes">{notes_str}</div>
            <div class="p-link">VIEW DETAILS ↗</div>
        </div>
    </a>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main App Logic ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv", cache_buster_v14="v14")

if df is not None:
    # Header
    st.markdown("<h1 style='text-align: center; font-family: Playfair Display; color: #D4AF37; margin-bottom: 5px;'>Perfume Finder</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 12px; margin-top: 0;'>LUXURY DATABASE</p>", unsafe_allow_html=True)
    
    st.write("") # Spacing
    
    # --- FILTERS ON MAIN PAGE (EXPANDER) ---
    # Replaces sidebar. Default expanded.
    with st.expander("🎛️ CLICK TO FILTER", expanded=True):
        
        # Gender (Horizontal Radio Buttons - Mobile Friendly)
        gender = st.radio("Gender:", ["Female", "Male", "Unisex"], horizontal=True)
        
        # Score (Slider)
        score = st.slider("Min Rating:", 1.0, 5.0, 4.0, 0.1)
        
        # Notes (Multiselect)
        notes = st.multiselect("Scent Notes:", unique_accords, placeholder="e.g. vanilla, rose...")
        
    # --- FILTERING ---
    filtered = df[df['gender'] == gender].copy()
    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_str):
            if pd.isna(row_str): return False
            row_list = [n.strip().strip("'\"").strip().lower() for n in row_str.strip("[]").split(",")]
            return all(note in row_list for note in notes)
        filtered = filtered[filtered['main_accords'].apply(check_notes)]

    # --- RESULTS ---
    st.markdown("---")
    st.markdown(f"<div style='margin-bottom: 15px; color: #888; font-size: 13px; text-align: center;'>FOUND: {len(filtered)}</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No results found for these criteria. Try changing filters.")
    else:
        # Display clean cards (limit 50 for performance)
        for row in filtered.head(50).itertuples():
            render_clean_card(row)
            
    st.markdown("<br><br><div style='text-align: center; color: #444; font-size: 10px;'>© 2024 Magdalena Romaniecka</div>", unsafe_allow_html=True)

else:
    st.error("Error: Could not load data.")