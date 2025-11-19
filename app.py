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

# --- 2. ANALYTICS ---
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

# --- 3. DATA LOGIC ---
def brutal_clean(text):
    if pd.isna(text): return []
    text = str(text)
    text = re.sub(r"[^a-zA-Z, ]", "", text)
    return [x.strip().upper() for x in text.split(",") if x.strip()]

def generate_stars(score):
    try:
        val = float(score)
        full = int(val)
        full = min(full, 5)
        return "★" * full + "☆" * (5 - full)
    except:
        return "☆☆☆☆☆"

def get_initials(name):
    if not name: return "PF"
    clean = re.sub(r"[^a-zA-Z0-9 ]", "", str(name))
    words = clean.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return clean[:2].upper()

# --- 4. CSS STYLING ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@600;700&display=swap');

        /* --- ELEGANT TITLE FRAME --- */
        .title-frame {
            border: 3px double #D4AF37;
            padding: 30px;
            margin-bottom: 40px;
            text-align: center;
            background: rgba(0, 0, 0, 0.3);
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
        }

        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {
            background-color: #050505 !important;
            border-right: 1px solid #222;
        }
        .stSidebar h2, .stSidebar h3 {
            font-family: 'Playfair Display', serif !important;
            font-size: 12px !important;
            color: #D4AF37 !important;
            margin-bottom: 5px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stSidebar label p {
            font-size: 11px !important;
            color: #AAA !important;
        }
        .stRadio, .stMultiSelect, .stSlider { margin-bottom: -20px !important; }
        div[role="radiogroup"] { gap: 0px !important; }
        
        /* --- DROPDOWN FIX --- */
        div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
            background-color: #0E0E0E !important;
            border: 1px solid #333 !important;
        }
        li[role="option"] {
             background-color: #0E0E0E !important;
             color: #E0E0E0 !important;
             font-size: 12px !important;
        }
        li[role="option"]:hover, li[role="option"][aria-selected="true"] {
            background-color: #D4AF37 !important;
            color: #000000 !important;
        }
        span[data-baseweb="tag"] {
            background-color: #222 !important;
            color: #D4AF37 !important;
            border: 1px solid #444 !important;
            font-size: 10px !important;
        }

        /* --- GENERAL STYLES --- */
        header, [data-testid="stHeader"] {
            background-color: #0E0E0E !important;
            border-bottom: 1px solid #333;
        }
        .stApp {
            background-color: #0E0E0E !important;
            background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 100%) !important;
        }
        * { font-family: 'Montserrat', sans-serif; color: #E0E0E0; }
        h1 { font-family: 'Playfair Display', serif; color: #D4AF37 !important; }
        
        div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
        div[data-testid="stMetricLabel"] { color: #888 !important; }

        /* BUTTON FRAGRANTICA */
        a.fragrantica-btn {
            display: inline-block;
            margin-top: 12px;
            padding: 6px 12px;
            border: 1px solid #D4AF37;
            border-radius: 4px;
            color: #D4AF37 !important;
            text-decoration: none;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        a.fragrantica-btn:hover {
            background-color: #D4AF37;
            color: #000000 !important;
        }

        [data-testid="stSidebarCollapsedControl"] {
            color: #D4AF37 !important;
            transform: scale(1.2);
            background: rgba(212, 175, 55, 0.1);
            border-radius: 5px;
        }
        hr { border-color: #333; margin: 1em 0; }
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

# --- 6. RENDER CARD ---
def render_gold_card(perfume):
    notes = perfume.clean_accords[:4]
    notes_str = " • ".join(notes) if notes else "Classic Blend"
    stars = generate_stars(perfume.score)
    initials = get_initials(perfume.name)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 3.5, 1.5])
        
        with col1:
            st.markdown(f"""
            <div style="
                width: 60px; height: 60px; 
                border: 2px solid #D4AF37; 
                border-radius: 50%; 
                background-color: #000;
                display: flex; align-items: center; justify-content: center;
                font-family: 'Playfair Display'; font-size: 22px; color: #D4AF37;
                box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
                margin: 0 auto;
            ">
                {initials}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 5px;">
                <span style="font-family: 'Playfair Display'; font-size: 18px; color: #FFF; letter-spacing: 0.5px;">
                    {perfume.name}
                </span>
            </div>
            <div style="font-size: 10px; color: #AAA; text-transform: uppercase;">
                <span style="color: #D4AF37; font-weight: bold;">NOTES:</span> {notes_str}
            </div>
            """, unsafe_allow_html=True)
            
            if pd.notna(perfume.img_link):
                st.markdown(f"""
                <a href='{perfume.img_link}' target='_blank' class='fragrantica-btn'>
                   VIEW ON FRAGRANTICA ↗
                </a>
                """, unsafe_allow_html=True)

        with col3:
            st.metric(label="SCORE", value=f"{perfume.score:.1f}", delta=stars)
        
        st.markdown("<hr style='margin: 15px 0; border-color: #222;'>", unsafe_allow_html=True)

# --- 7. MAIN APP ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    with st.sidebar:
        # CHANGED TO "CATEGORY"
        st.markdown("### CATEGORY")
        gender = st.radio("gender_select", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        st.write("")
        st.markdown("### NOTES")
        notes = st.multiselect("notes_select", unique_accords, placeholder="Select...", label_visibility="collapsed")
        
        st.write("")
        st.markdown("### RATING")
        score = st.slider("rating_slider", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align:center; font-size:9px; color:#555; line-height:1.6;'>
            DATA SOURCE: FRAGRANTICA (KAGGLE)<br>
            © 2025 MAGDALENA ROMANIECKA
        </div>
        """, unsafe_allow_html=True)

    # HEADER WITH ELEGANT FRAME
    st.markdown("""
    <div class="title-frame">
        <h1 style='margin-bottom: 5px; font-size: 42px; letter-spacing: 5px;'>PERFUME FINDER</h1>
        <p style='color:#888; font-size:11px; letter-spacing:4px; margin:0; text-transform: uppercase;'>
            Luxury Fragrance Database
        </p>
    </div>
    """, unsafe_allow_html=True)

    if gender == "All": filtered = df.copy()
    else: filtered = df[df['gender'] == gender].copy()
    
    filtered = filtered[filtered['score'] >= score]
    if notes:
        filtered = filtered[filtered['clean_accords'].apply(lambda x: all(n in x for n in notes))]

    st.markdown(f"<center style='color:#444; font-size:11px; margin-bottom:20px;'>{len(filtered)} RESULTS FOUND</center>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No perfumes found.")
    else:
        for row in filtered.head(40).itertuples():
            render_gold_card(row)
else:
    st.error("Error loading database.")