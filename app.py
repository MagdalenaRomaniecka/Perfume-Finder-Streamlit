import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
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
        return "★" * full_stars + "☆" * (5 - full_stars)
    except:
        return "☆☆☆☆☆"

# --- 4. CSS STYLING (NATIVE THEME) ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@600;700&display=swap');

        /* MAIN BACKGROUND */
        .stApp {
            background-color: #0E0E0E !important;
            background-image: radial-gradient(circle at 50% 0%, #1c1c1c 0%, #000000 100%) !important;
            background-attachment: fixed !important;
        }

        /* HIDE HEADER / FIX SIDEBAR ARROW */
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="collapsedControl"] { color: #D4AF37 !important; }

        /* TYPOGRAPHY */
        * { font-family: 'Montserrat', sans-serif; color: #E0E0E0; }
        h1, h2, h3 { font-family: 'Playfair Display', serif; color: #D4AF37 !important; }
        
        /* METRIC STYLING (The Rating Box) */
        div[data-testid="stMetricValue"] {
            color: #D4AF37 !important;
            font-size: 26px !important;
            font-family: 'Playfair Display', serif !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #888 !important;
            font-size: 10px !important;
            letter-spacing: 2px;
        }
        div[data-testid="stMetricDelta"] {
            color: #D4AF37 !important; /* Gold Stars */
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #050505 !important;
            border-right: 1px solid #222;
        }
        
        /* DIVIDER */
        hr { margin: 2em 0; border-color: #333; }
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

# --- 6. CARD RENDERING (STABLE NATIVE) ---
def render_native_card(perfume):
    # Prepare Data
    notes = perfume.clean_accords[:4]
    notes_str = " • ".join(notes) if notes else "Classic Blend"
    stars = generate_stars(perfume.score)
    initial = perfume.name[0].upper() if perfume.name else "P"
    
    # LAYOUT: Native Columns (Safe & Stable)
    with st.container():
        # Layout: Monogram (Small) | Content (Wide) | Score (Medium)
        col1, col2, col3 = st.columns([1, 4, 2])
        
        with col1:
            # Simple Monogram
            st.markdown(f"<h1 style='text-align:center; font-size:40px; margin:0; color:#D4AF37;'>{initial}</h1>", unsafe_allow_html=True)
        
        with col2:
            # Name & Notes
            st.markdown(f"<h3 style='margin:0; font-size:18px; color:#FFF;'>{perfume.name}</h3>", unsafe_allow_html=True)
            st.caption(f"NOTES: {notes_str}")
            
            if pd.notna(perfume.img_link):
                st.markdown(f"<a href='{perfume.img_link}' target='_blank' style='font-size:10px; color:#666; text-decoration:none;'>VIEW DETAILS ></a>", unsafe_allow_html=True)

        with col3:
            # Native Metric for Rating
            st.metric(label="RATING", value=f"{perfume.score:.1f}", delta=stars)
            
        # Divider Line
        st.divider()

# --- 7. MAIN APPLICATION ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    # SIDEBAR FILTERS
    with st.sidebar:
        st.header("FIND YOUR SCENT")
        gender = st.radio("AUDIENCE", ["All", "Female", "Male", "Unisex"])
        st.write("---")
        notes = st.multiselect("PREFERRED NOTES", unique_accords)
        st.write("---")
        score = st.slider("MIN RATING", 1.0, 5.0, 4.0, 0.1)
        st.markdown("---")
        st.caption("© 2024 Magdalena Romaniecka")

    # HEADER
    st.markdown("<h1 style='text-align:center; font-size: 42px; margin-bottom: 0;'>PERFUME FINDER</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:12px; letter-spacing:3px; margin-bottom:40px;'>EXCLUSIVE FRAGRANCE DATABASE</p>", unsafe_allow_html=True)

    # LOGIC
    if gender == "All": filtered = df.copy()
    else: filtered = df[df['gender'] == gender].copy()
    
    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        filtered = filtered[filtered['clean_accords'].apply(lambda x: all(n in x for n in notes))]

    # RESULTS
    st.markdown(f"<center style='color:#666; font-size:12px; margin-bottom:30px;'>FOUND {len(filtered)} FRAGRANCES</center>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No perfumes found. Try adjusting your filters.")
    else:
        for row in filtered.head(40).itertuples():
            render_native_card(row)
else:
    st.error("Error: Database not found.")