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
    text = re.sub(r"[^a-zA-Z, ]", "", text)
    return [x.strip().upper() for x in text.split(",") if x.strip()]

def generate_stars(score):
    try:
        val = float(score)
        full_stars = int(val)
        full_stars = min(full_stars, 5)
        empty_stars = 5 - full_stars
        return "★" * full_stars + "☆" * empty_stars
    except:
        return "☆☆☆☆☆"

# --- 4. CSS STYLING (FIXED NAVIGATION) ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@600;700&display=swap');

        /* Main Background */
        .stApp {
            background-color: #0E0E0E !important;
            background-image: radial-gradient(circle at 50% 0%, #1c1c1c 0%, #000000 100%) !important;
            background-attachment: fixed !important;
        }

        /* --- NAVIGATION FIX (SIDEBAR BUTTON) --- */
        /* Make header transparent instead of hidden */
        [data-testid="stHeader"] {
            background: transparent !important;
            color: #D4AF37 !important; 
        }
        
        /* Style the Expand/Collapse Button (The Arrow) */
        [data-testid="collapsedControl"] {
            color: #D4AF37 !important; /* Gold Arrow */
            background-color: rgba(255, 255, 255, 0.05) !important; /* Subtle background */
            border: 1px solid #D4AF37 !important;
            border-radius: 8px !important;
            margin-top: 10px;
            transition: transform 0.2s;
        }
        [data-testid="collapsedControl"]:hover {
            transform: scale(1.1);
            background-color: rgba(212, 175, 55, 0.2) !important;
        }
        
        /* Global Typography */
        h1, h2, h3, p, label, span, div {
            color: #E0E0E0 !important;
            font-family: 'Montserrat', sans-serif;
        }

        /* Title */
        .title-box {
            text-align: center;
            padding: 30px 0;
            margin-bottom: 40px;
            border-bottom: 1px solid #333;
        }
        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: 36px !important;
            color: #D4AF37 !important;
            letter-spacing: 3px;
            margin: 0;
            text-transform: uppercase;
        }
        .sub-title {
            font-size: 10px !important;
            color: #888 !important;
            letter-spacing: 4px;
            margin-top: 8px;
            text-transform: uppercase;
        }

        /* Card Design */
        .perfume-card {
            background-color: #121212;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: transform 0.2s;
        }
        .perfume-card:hover {
            border-color: #D4AF37;
            background-color: #181818;
            transform: translateY(-2px);
        }

        /* Monogram */
        .monogram {
            width: 60px;
            height: 60px;
            min-width: 60px;
            background: #000;
            border: 1px solid #D4AF37;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Playfair Display', serif;
            font-size: 28px;
            color: #D4AF37;
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.15);
        }

        /* Card Info */
        .card-content { flex-grow: 1; overflow: hidden; }
        .card-name {
            font-family: 'Playfair Display', serif;
            font-size: 16px !important;
            color: #FFF !important;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .card-notes {
            font-size: 10px !important;
            color: #AAA !important;
            line-height: 1.4;
        }
        .highlight { color: #D4AF37 !important; font-weight: 600; }

        /* Rating */
        .card-rating {
            text-align: center;
            min-width: 70px;
            border-left: 1px solid #333;
            padding-left: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .rating-val {
            font-size: 18px !important;
            color: #D4AF37 !important;
            font-weight: 700;
        }
        .rating-stars {
            color: #D4AF37 !important;
            font-size: 10px !important;
            letter-spacing: 1px;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #080808 !important;
            border-right: 1px solid #222;
        }
        .stRadio label, .stMultiSelect label, .stSlider label {
            color: #D4AF37 !important;
            font-size: 12px !important;
        }
        
        @media (max-width: 600px) {
            .perfume-card { flex-direction: column; text-align: center; padding: 20px; }
            .card-rating { border-left: none; border-top: 1px solid #333; padding-top: 15px; padding-left: 0; width: 100%; margin-top: 10px; }
            .monogram { margin: 0 auto 10px auto; }
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
        
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(lambda row: str(row['name']).replace(str(row['gender']), '').strip() if pd.notna(row['name']) else row['name'], axis=1)
        
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        df.dropna(subset=['main_accords', 'name', 'gender'], inplace=True)
        
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        df['clean_accords'] = df['main_accords'].apply(brutal_clean)
        
        all_accords = set()
        for accords_list in df['clean_accords']:
            for note in accords_list: all_accords.add(note)
        
        return df, sorted(list(all_accords))
    except:
        return None, []

def render_card(perfume):
    notes = perfume.clean_accords[:4]
    notes_str = " • ".join(notes) if notes else "Classic Blend"
    stars = generate_stars(perfume.score)
    initial = perfume.name[0].upper() if perfume.name else "P"
    
    html_code = f"""
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
    st.markdown(html_code, unsafe_allow_html=True)

# --- 6. MAIN APP ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    with st.sidebar:
        st.markdown("### FIND YOUR SCENT")
        st.write("")
        gender = st.radio("AUDIENCE", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        st.write("")
        st.markdown("NOTES")
        notes = st.multiselect("notes_sel", unique_accords, placeholder="Choose notes...", label_visibility="collapsed")
        st.write("")
        st.markdown("RATING")
        score = st.slider("rate_slider", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        st.markdown("---")
        st.markdown("<div style='text-align:center; font-size:10px; color:#555'>© 2024 Magdalena Romaniecka</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class="title-box">
            <h1 class="main-title">Perfume Finder</h1>
            <div class="sub-title">Exclusive Fragrance Database</div>
        </div>
    """, unsafe_allow_html=True)

    if gender == "All": filtered = df.copy()
    else: filtered = df[df['gender'] == gender].copy()
    
    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        filtered = filtered[filtered['clean_accords'].apply(lambda x: all(n in x for n in notes))]

    st.markdown(f"<div style='text-align:center; color:#666; margin-bottom:20px; font-size:12px'>FOUND {len(filtered)} FRAGRANCES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No perfumes found.")
    else:
        for row in filtered.head(40).itertuples():
            render_card(row)
else:
    st.error("Error: Database not found.")