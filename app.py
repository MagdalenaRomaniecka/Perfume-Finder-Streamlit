import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. ANALYTICS (GA4) ---
def inject_ga4():
    GA_ID = "G-S5NLHL3KFM"
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>
    """
    components.html(ga_code, height=0, width=0)

inject_ga4()

# --- 3. DATA CLEANING ---
def brutal_clean(text):
    if pd.isna(text): return []
    text = str(text)
    # Remove all special characters except text and commas
    text = re.sub(r"[^a-zA-Z, ]", "", text)
    return [x.strip().upper() for x in text.split(",") if x.strip()]

def generate_stars(score):
    full_stars = int(score)
    empty_stars = 5 - full_stars
    return "★" * full_stars + "☆" * empty_stars

# --- 4. CSS STYLING (MONOGRAM EDITION) ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@600;700&display=swap');

        /* Force Dark Background */
        .stApp {
            background-color: #0E0E0E !important;
            background-image: radial-gradient(circle at 50% 0%, #1c1c1c 0%, #000000 100%) !important;
        }

        /* Hide Streamlit Elements */
        [data-testid="stHeader"] { display: none; }
        
        /* Global Text Colors */
        h1, h2, h3, p, label, span, div {
            color: #E0E0E0 !important;
            font-family: 'Montserrat', sans-serif;
        }

        /* TITLE SECTION */
        .title-box {
            text-align: center;
            padding: 30px;
            margin-bottom: 30px;
            border-bottom: 1px solid #333;
        }
        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: 38px !important;
            color: #D4AF37 !important;
            letter-spacing: 3px;
            margin: 0;
            text-transform: uppercase;
        }
        .sub-title {
            font-size: 10px !important;
            color: #888 !important;
            letter-spacing: 5px;
            margin-top: 5px;
            text-transform: uppercase;
        }

        /* PERFUME CARD (Flexbox Layout) */
        .perfume-card {
            background-color: #121212;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 20px;
            transition: transform 0.2s;
        }
        .perfume-card:hover {
            border-color: #D4AF37;
            background-color: #181818;
            transform: translateY(-3px);
        }

        /* MONOGRAM (Replaces Broken Images) */
        .monogram {
            width: 70px;
            height: 70px;
            min-width: 70px; /* Prevent shrinking */
            background: #000;
            border: 2px solid #D4AF37;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Playfair Display', serif;
            font-size: 30px;
            color: #D4AF37;
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
        }

        /* CONTENT SECTION */
        .card-content {
            flex-grow: 1;
            overflow: hidden;
        }
        .card-name {
            font-family: 'Playfair Display', serif;
            font-size: 18px !important;
            color: #FFF !important;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .card-notes {
            font-size: 11px !important;
            color: #AAA !important;
            line-height: 1.4;
        }
        .highlight { color: #D4AF37 !important; font-weight: 600; }

        /* RATING SECTION */
        .card-rating {
            text-align: center;
            min-width: 80px;
            border-left: 1px solid #333;
            padding-left: 15px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .rating-val {
            font-size: 22px !important;
            color: #D4AF37 !important;
            font-weight: 700;
        }
        .rating-stars {
            color: #D4AF37 !important;
            font-size: 12px !important;
            letter-spacing: 1px;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #080808 !important;
            border-right: 1px solid #222;
        }
        .stRadio label, .stMultiSelect label, .stSlider label {
            color: #D4AF37 !important;
            font-size: 12px !important;
        }

        /* MOBILE FIXES */
        @media (max-width: 600px) {
            .perfume-card { flex-direction: column; text-align: center; }
            .card-rating { border-left: none; border-top: 1px solid #333; padding-top: 15px; padding-left: 0; width: 100%; }
            .monogram { margin: 0 auto; }
            .card-name { white-space: normal; }
        }
        </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOADING ---
@st.cache_data
def load_data(filepath): 
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Name Logic
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(lambda row: str(row['name']).replace(str(row['gender']), '').strip() if pd.notna(row['name']) else row['name'], axis=1)
        
        # Gender Logic
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # Cleanup
        df.dropna(subset=['main_accords', 'name', 'gender'], inplace=True)
        
        # Score Logic
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # Accord Logic
        df['clean_accords'] = df['main_accords'].apply(brutal_clean)
        
        # Unique Notes
        all_accords = set()
        for accords_list in df['clean_accords']:
            for note in accords_list: all_accords.add(note)
        
        return df, sorted(list(all_accords))
    except:
        return None, []

def render_card(perfume):
    # Extract Data
    notes = perfume.clean_accords[:4]
    notes_str = " • ".join(notes) if notes else "Classic Blend"
    stars = generate_stars(perfume.score)
    
    # Create Monogram (First Letter)
    initial = perfume.name[0].upper() if perfume.name else "P"
    
    # HTML Structure
    html = f"""
    <div class="perfume-card">
        <div class="monogram">{initial}</div>
        
        <div class="card-content">
            <div class="card-name">{perfume.name}</div>
            <div class="card-notes">
                <span class="highlight">NOTES:</span> {notes_str}
            </div>
        </div>
        
        <div class="card-rating">
            <div class="rating-val">{perfume.score:.1f}</div>
            <div class="rating-stars">{stars}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 6. MAIN APP ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    # SIDEBAR
    with st.sidebar:
        st.markdown("### FIND YOUR SCENT")
        st.write("")
        
        # Gender
        gender = st.radio("AUDIENCE", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        st.write("")
        
        # Notes
        st.markdown("NOTES")
        notes = st.multiselect("notes_sel", unique_accords, placeholder="Choose notes...", label_visibility="collapsed")
        st.write("")
        
        # Rating
        st.markdown("MIN RATING")
        score = st.slider("rate", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("<div style='text-align:center; font-size:10px; color:#555'>© 2024 Magdalena Romaniecka</div>", unsafe_allow_html=True)

    # HEADER
    st.markdown("""
        <div class="title-box">
            <h1 class="main-title">Perfume Finder</h1>
            <div class="sub-title">Exclusive Fragrance Database</div>
        </div>
    """, unsafe_allow_html=True)

    # LOGIC
    if gender == "All": filtered = df.copy()
    else: filtered = df[df['gender'] == gender].copy()
    
    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        filtered = filtered[filtered['clean_accords'].apply(lambda x: all(n in x for n in notes))]

    # OUTPUT
    st.markdown(f"<div style='text-align:center; color:#666; margin-bottom:20px; font-size:12px'>FOUND {len(filtered)} FRAGRANCES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No perfumes found. Try adjusting filters.")
    else:
        for row in filtered.head(40).itertuples():
            render_card(row)
else:
    st.error("Error: Database not found.")