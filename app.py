import streamlit as st
import pandas as pd
import re
import ast
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
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

def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #0E0E0E; 
        }
        [data-testid="stAppViewContainer"] { background-color: #0E0E0E; }
        [data-testid="stHeader"] { display: none; }

        section[data-testid="stSidebar"] {
            background-color: #111; 
            border-right: 1px solid #333;
        }
        
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #D4AF37 !important;
            font-family: 'Playfair Display', serif;
            margin-bottom: 10px !important;
        }

        div[role="radiogroup"] label {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            padding: 10px 12px !important;
            border-radius: 6px !important;
            margin-bottom: 6px !important;
            transition: all 0.2s ease-in-out;
        }
        
        div[role="radiogroup"] label p {
            font-size: 13px !important;
            color: #BBBBBB !important; 
            font-weight: 500 !important;
        }

        div[role="radiogroup"] label:has(input:checked) {
            background-color: #D4AF37 !important;
            border-color: #D4AF37 !important;
            transform: scale(1.02);
        }
        
        div[role="radiogroup"] label:has(input:checked) p {
            color: #000000 !important;
            font-weight: 800 !important;
        }
        
        div[role="radiogroup"] label div[data-baseweb="radio"] { display: none; }

        div[data-testid="stSlider"] label p { color: #FFF !important; font-size: 13px; }
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p { color: #D4AF37 !important; font-weight:700; }
        div[data-testid="stSlider"] .st-ae { background-color: #D4AF37 !important; }

        .perfume-container {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #222;
        }

        .info-row {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            align-items: stretch;
        }

        .box-name {
            flex-grow: 1;
            background-color: #161616;
            border: 1px solid #333;
            border-left: 3px solid #D4AF37;
            padding: 15px;
            border-radius: 4px;
            display: flex;
            align-items: center;
        }
        .name-text {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #FFF;
            font-weight: 600;
            line-height: 1.2;
        }

        .box-rating {
            background-color: #D4AF37;
            color: #000;
            min-width: 70px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 4px;
            padding: 5px;
        }
        .rating-num {
            font-size: 18px;
            font-weight: 800;
        }
        .rating-sub {
            font-size: 9px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .notes-row {
            font-size: 11px;
            color: #888;
            margin-bottom: 10px;
            padding-left: 5px;
        }
        .note-highlight {
            color: #CCC;
            font-style: italic;
        }

        .fragrantica-link {
            display: block;
            text-align: right;
            font-size: 10px;
            color: #D4AF37;
            text-decoration: none;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .fragrantica-link:hover {
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)

def parse_accords_safe(row_data):
    try:
        if pd.isna(row_data): return []
        if str(row_data).strip().startswith("["):
            try:
                parsed = ast.literal_eval(str(row_data))
                if isinstance(parsed, list):
                    return [str(item).strip().lower() for item in parsed]
            except:
                pass
        
        clean_text = re.sub(r"[\[\]'\"]", "", str(row_data))
        return [item.strip().lower() for item in clean_text.split(",") if item.strip()]
    except:
        return []

@st.cache_data
def load_data(filepath): 
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
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
            
        df['clean_accords']