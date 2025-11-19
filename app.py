import streamlit as st
import pandas as pd
import re
import ast
import streamlit.components.v1 as components

# --- 1. Konfiguracja strony (Musi byc pierwsza) ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. Google Analytics (Twoj kod G-S5NLHL3KFM) ---
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

# --- 3. Style CSS (Dark Luxury) ---
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

# --- 4. Funkcje pomocnicze ---
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

def render_modular_card(perfume):
    notes_list = perfume.clean_accords[:5]
    notes_str = ", ".join(notes_list) if notes_list else "N/A"

    html = f"""
    <div class="perfume-container">
        <div class="info-row">
            <div class="box-name">
                <div class="name-text">{perfume.name}</div>
            </div>
            <div class="box-rating">
                <div class="rating-num">{perfume.score:.1f}</div>
                <div class="rating-sub">SCORE</div>
            </div>
        </div>
        
        <div class="notes-row">
            NOTES: <span class="note-highlight">{notes_str}</span>
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="fragrantica-link">
            VIEW ON FRAGRANTICA ↗
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 5. Ladowanie Danych (To tu byl blad) ---
@st.cache_data
def load_data(filepath): 
    try:
        df = pd.read_csv(filepath)
        # Zmiana nazw kolumn
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Czyszczenie nazwy
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
        
        # Mapowanie plci
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        
        # Usuwanie pustych
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # Naprawa formatu liczb (zamiana przecinka na kropke)
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # Parsowanie akordow
        df['clean_accords'] = df['main_accords'].apply(parse_accords_safe)
        
        # Zbieranie unikalnych nut
        all_accords = set()
        for accords_list in df['clean_accords']:
            for note in accords_list:
                all_accords.add(note)
        
        return df, sorted(list(all_accords))
    except Exception as e:
        # W razie bledu zwroc puste wartosci
        return None, []

# --- 6. Glowna Aplikacja ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    
    # Sidebar
    with st.sidebar:
        st.markdown("### FILTER SEARCH")
        st.write("")
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("**MIN RATING**")
        score = st.slider("min_rating", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("**SCENT NOTES**")
        notes = st.multiselect("scent_notes", unique_accords, placeholder="Type ingredient...", label_visibility="collapsed")
        
        st.markdown("<br><br><div style='color:#444; font-size:10px'>© 2024 Portfolio</div>", unsafe_allow_html=True)

    # Main Content
    st.markdown("<h1 style='text-align: center; font-family: Playfair Display; color: #D4AF37; margin-bottom: 0;'>PERFUME FINDER</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #666; font-size: 11px; margin-bottom: 30px; letter-spacing: 2px;'>LUXURY DATABASE</div>", unsafe_allow_html=True)

    # Logic
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_list):
            return all(note in row_list for note in notes)
        filtered = filtered[filtered['clean_accords'].apply(check_notes)]

    # Results
    st.markdown(f"<div style='color: #888; font-size: 12px; margin-bottom: 15px; border-bottom: 1px solid #222; padding-bottom: 5px;'>FOUND {len(filtered)} MATCHES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        for row in filtered.head(50).itertuples():
            render_modular_card(row)

else:
    st.error("Data Error. Please check if fra_perfumes.csv exists.")