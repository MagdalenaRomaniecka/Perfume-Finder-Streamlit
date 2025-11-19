import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Perfume Finder",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded"
)

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

def brutal_clean(text):
    if pd.isna(text): return []
    text = str(text)
    text = re.sub(r"[^a-zA-Z, ]", "", text)
    return [x.strip().upper() for x in text.split(",") if x.strip()]

def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Cinzel:wght@500;700&display=swap');

        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 50% 20%, #1a1a2e 0%, #000000 100%);
            color: #E0E0E0;
        }
        [data-testid="stHeader"] { display: none; }

        .title-box {
            border-top: 4px solid #D4AF37;
            border-bottom: 4px solid #D4AF37;
            padding: 30px;
            text-align: center;
            margin-bottom: 50px;
            background: rgba(0, 0, 0, 0.4);
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.1);
        }
        .main-title {
            font-family: 'Cinzel', serif;
            color: #D4AF37;
            font-size: 36px;
            letter-spacing: 6px;
            margin: 0;
            text-transform: uppercase;
            font-weight: 700;
        }
        .sub-title {
            font-family: 'Montserrat', sans-serif;
            color: #AAA;
            font-size: 11px;
            letter-spacing: 3px;
            margin-top: 10px;
            text-transform: uppercase;
        }

        .perfume-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 25px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            max-width: 750px;
            margin-left: auto;
            margin-right: auto;
        }
        .perfume-card:hover {
            border-color: #D4AF37;
            background: rgba(255, 255, 255, 0.06);
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        }

        .card-img {
            width: 85px;
            height: 85px;
            object-fit: contain;
            background: #FFF;
            border-radius: 50%;
            padding: 5px;
            border: 2px solid #222;
        }

        .card-content { flex-grow: 1; }
        
        .card-name {
            font-family: 'Cinzel', serif;
            font-size: 20px;
            color: #FFF;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .card-notes {
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            color: #BBB;
            line-height: 1.6;
        }
        .highlight { color: #D4AF37; font-weight: 600; }

        .card-score {
            text-align: center;
            border-left: 1px solid #333;
            padding-left: 20px;
            min-width: 70px;
        }
        .score-val { font-size: 24px; font-weight: 700; color: #D4AF37; }
        .score-label { font-size: 9px; color: #666; letter-spacing: 1px; margin-top: 2px; }

        .card-link {
            display: inline-block;
            font-size: 9px;
            color: #888;
            text-decoration: none;
            margin-top: 10px;
            border: 1px solid #333;
            padding: 4px 10px;
            border-radius: 20px;
            transition: 0.3s;
        }
        .card-link:hover { color: #D4AF37; border-color: #D4AF37; }

        section[data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #222;
        }
        
        .stRadio label, .stMultiSelect label, .stSlider label {
            color: #D4AF37 !important;
            font-family: 'Montserrat', sans-serif;
            font-size: 12px !important;
            letter-spacing: 1px;
        }
        
        .stMultiSelect span { color: #E0E0E0; }

        @media only screen and (max-width: 600px) {
            .perfume-card { flex-direction: column; text-align: center; gap: 15px; padding: 15px; }
            .card-score { border-left: none; border-top: 1px solid #333; padding-top: 15px; padding-left: 0; width: 100%; }
            .main-title { font-size: 26px; letter-spacing: 3px; }
            .card-img { width: 70px; height: 70px; }
        }
        </style>
    """, unsafe_allow_html=True)

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

def render_luxury_card(perfume):
    notes = perfume.clean_accords[:4]
    notes_str = " • ".join(notes) if notes else "Classic Blend"
    
    img_url = perfume.img_link if pd.notna(perfume.img_link) else "https://cdn-icons-png.flaticon.com/512/3050/3050253.png"

    html = f"""
    <div class="perfume-card">
        <img src="{img_url}" class="card-img" onerror="this.style.display='none'">
        <div class="card-content">
            <div class="card-name">{perfume.name}</div>
            <div class="card-notes">
                <span class="highlight">NOTES:</span> {notes_str}
            </div>
            <a href="{img_url}" target="_blank" class="card-link">VIEW DETAILS</a>
        </div>
        <div class="card-score">
            <div class="score-val">{perfume.score:.1f}</div>
            <div class="score-label">RATING</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    with st.sidebar:
        st.markdown("### FIND YOUR SCENT")
        st.write("")
        
        gender = st.radio("TARGET AUDIENCE", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        st.write("")
        
        st.markdown("PREFERRED NOTES")
        notes = st.multiselect("notes_selector", unique_accords, placeholder="e.g. Vanilla, Oud...", label_visibility="collapsed")
        st.write("")

        st.markdown("MIN RATING")
        score = st.slider("rating_slider", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("<div style='text-align:center; color:#444; font-size:10px'>DESIGNED BY MAGDALENA ROMANIECKA</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class="title-box">
            <h1 class="main-title">Perfume Finder</h1>
            <div class="sub-title">Curated Fragrance Collection</div>
        </div>
    """, unsafe_allow_html=True)

    if gender == "All": filtered = df.copy()
    else: filtered = df[df['gender'] == gender].copy()
    
    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        filtered = filtered[filtered['clean_accords'].apply(lambda x: all(n in x for n in notes))]

    st.markdown(f"<div style='text-align: center; color: #666; font-size: 12px; margin-bottom: 30px;'>DISCOVERED {len(filtered)} FRAGRANCES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No matches found. Try selecting fewer notes or a lower rating.")
    else:
        for row in filtered.head(40).itertuples():
            render_luxury_card(row)

else:
    st.error("Could not load database.")