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
    """Creates a 2-letter elegant abbreviation (e.g., 'Chanel No 5' -> 'CN')"""
    if not name: return "PF"
    # Clean name and split
    clean_name = re.sub(r"[^a-zA-Z0-9 ]", "", str(name))
    words = clean_name.split()
    
    if len(words) >= 2:
        # First letter of first two words
        return (words[0][0] + words[1][0]).upper()
    else:
        # First two letters of the single word
        return clean_name[:2].upper()

# --- 4. CSS STYLING (DROPDOWN FIX & FRAMES) ---
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

        /* --- CRITICAL FIX: DROPDOWN MENU VISIBILITY --- */
        /* This targets the pop-up list when you click Select/Multiselect */
        div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
            background-color: #111 !important;
            border: 1px solid #333 !important;
        }
        
        /* The options inside the list */
        li[role="option"] {
             background-color: #111 !important;
             color: #E0E0E0 !important;
        }
        
        /* Selected option or Hover state */
        li[role="option"]:hover, li[aria-selected="true"] {
            background-color: #D4AF37 !important;
            color: #000 !important;
            font-weight: bold !important;
        }
        
        /* The tags inside the box after selection */
        span[data-baseweb="tag"] {
            background-color: #222 !important;
            color: #D4AF37 !important;
            border: 1px solid #444 !important;
        }

        /* --- END DROPDOWN FIX --- */

        /* TYPOGRAPHY */
        * { font-family: 'Montserrat', sans-serif; color: #E0E0E0; }
        h1, h2, h3 { font-family: 'Playfair Display', serif; color: #D4AF37 !important; }
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="collapsedControl"] { color: #D4AF37 !important; }

        /* TITLE */
        .title-box {
            text-align: center;
            padding: 40px 0;
            margin-bottom: 40px;
            border-bottom: 1px solid #333;
            border-top: 1px solid #333;
            background: rgba(0,0,0,0.2);
        }
        .main-title {
            font-size: 42px !important;
            letter-spacing: 4px;
            margin: 0;
            text-transform: uppercase;
        }
        .sub-title {
            font-size: 10px !important;
            color: #888 !important;
            letter-spacing: 5px;
            margin-top: 10px;
            text-transform: uppercase;
        }

        /* CARD DESIGN (WITH GOLD FRAME) */
        .perfume-card {
            background-color: #121212;
            border: 1px solid #333; /* Subtle border */
            border-left: 4px solid #D4AF37; /* Gold accent on left */
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 20px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .perfume-card:hover {
            border-color: #D4AF37; /* Full gold border on hover */
            background-color: #161616;
            transform: translateX(5px);
        }

        /* MONOGRAM CIRCLE */
        .monogram {
            min-width: 65px;
            height: 65px;
            background: #050505;
            border: 1px solid #D4AF37;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Playfair Display', serif;
            font-size: 24px;
            color: #D4AF37;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
        }

        /* TEXT CONTENT */
        .card-content { flex-grow: 1; }
        .card-name {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFF;
            margin-bottom: 5px;
            letter-spacing: 0.5px;
        }
        .card-notes {
            font-size: 10px;
            color: #AAA;
            line-height: 1.5;
            text-transform: uppercase;
        }
        .highlight { color: #D4AF37; font-weight: 600; }

        /* RATING BOX */
        .card-rating {
            text-align: center;
            min-width: 80px;
            border-left: 1px solid #333;
            padding-left: 15px;
        }
        .rating-val { font-size: 22px; color: #D4AF37; font-weight: 700; font-family: 'Playfair Display', serif; }
        .rating-stars { color: #D4AF37; font-size: 12px; letter-spacing: 2px; margin-top: 5px; }

        /* SIDEBAR */
        section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #222; }
        .stRadio label, .stMultiSelect label, .stSlider label { color: #D4AF37 !important; font-size: 12px !important; }
        
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
    
    # Generate 2-letter initials
    initials = get_initials(perfume.name)
    
    # Use Safe HTML Rendering
    html = f"""
    <div class="perfume-card">
        <div class="monogram">{initials}</div>
        
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
        st.header("FIND YOUR SCENT")
        gender = st.radio("AUDIENCE", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        st.write("---")
        notes = st.multiselect("PREFERRED NOTES", unique_accords)
        st.write("---")
        score = st.slider("MIN RATING", 1.0, 5.0, 4.0, 0.1)
        st.markdown("---")
        st.caption("© 2024 Magdalena Romaniecka")

    # HEADER
    st.markdown("""
        <div class="title-box">
            <h1 class="main-title">Perfume Finder</h1>
            <div class="sub-title">The Gold Standard Database</div>
        </div>
    """, unsafe_allow_html=True)

    # LOGIC
    if gender == "All": filtered = df.copy()
    else: filtered = df[df['gender'] == gender].copy()
    filtered = filtered[filtered['score'] >= score]
    if notes:
        filtered = filtered[filtered['clean_accords'].apply(lambda x: all(n in x for n in notes))]

    # RESULTS
    st.markdown(f"<div style='text-align:center; color:#666; margin-bottom:30px; font-size:12px'>FOUND {len(filtered)} FRAGRANCES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No perfumes found. Try adjusting filters.")
    else:
        for row in filtered.head(40).itertuples():
            render_card(row)
else:
    st.error("Error: Database not found.")