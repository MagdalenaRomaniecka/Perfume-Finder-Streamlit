import streamlit as st
import pandas as pd
import re
import ast
import streamlit.components.v1 as components

# --- 1. Konfiguracja strony ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. Google Analytics (Twój kod G-S5NLHL3KFM) ---
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

# --- 3. Style CSS (Poprawiony Kontrast) ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        /* Tło i czcionka ogólna */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #F0F0F0 !important; /* Jaśniejsza biel */
            background-color: #0E0E0E; 
        }
        [data-testid="stAppViewContainer"] { background-color: #0E0E0E; }
        [data-testid="stHeader"] { display: none; }

        /* Pasek boczny */
        section[data-testid="stSidebar"] {
            background-color: #111; 
            border-right: 1px solid #333;
        }
        
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #D4AF37 !important;
            font-family: 'Playfair Display', serif;
            margin-bottom: 15px !important;
        }

        /* --- POPRAWA: Wybór Płci (Radio) - Wyraźniejsza czcionka --- */
        div[role="radiogroup"] label {
            background-color: #1A1A1A !important;
            border: 1px solid #444 !important; /* Jaśniejsza ramka */
            padding: 12px 15px !important; /* Większy przycisk */
            border-radius: 8px !important;
            margin-bottom: 8px !important;
        }
        
        /* Tekst niezaznaczony - TERAZ JAŚNIEJSZY */
        div[role="radiogroup"] label p {
            font-size: 15px !important; /* Większa czcionka */
            color: #FFFFFF !important; /* Czysta biel */
            font-weight: 600 !important; /* Pogrubienie */
        }

        /* Stan zaznaczony */
        div[role="radiogroup"] label:has(input:checked) {
            background-color: #D4AF37 !important;
            border-color: #FFD700 !important;
        }
        
        div[role="radiogroup"] label:has(input:checked) p {
            color: #000000 !important;
            font-weight: 900 !important; /* Extra Bold */
        }
        
        div[role="radiogroup"] label div[data-baseweb="radio"] { display: none; }

        /* --- POPRAWA: Suwak (Slider) --- */
        div[data-testid="stSlider"] label {
             color: #D4AF37 !important;
             font-weight: bold;
             font-size: 14px;
        }
        /* Liczby nad suwakiem */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p { 
            color: #FFF !important; 
            font-weight: 700;
            font-size: 16px !important;
        }
        /* Sam suwak */
        div[data-testid="stSlider"] .st-ae { background-color: #D4AF37 !important; }

        /* Karty Perfum */
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
            border-left: 4px solid #D4AF37;
            padding: 15px;
            border-radius: 4px;
            display: flex;
            align-items: center;
        }
        .name-text {
            font-family: 'Playfair Display', serif;
            font-size: 20px; /* Większa nazwa */
            color: #FFF;
            font-weight: 600;
            line-height: 1.2;
        }

        .box-rating {
            background-color: #D4AF37;
            color: #000;
            min-width: 75px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 4px;
            padding: 5px;
        }
        .rating-num {
            font-size: 20px;
            font-weight: 800;
        }
        .rating-sub {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .notes-row {
            font-size: 12px;
            color: #AAA; /* Jaśniejszy szary */
            margin-bottom: 10px;
            padding-left: 5px;
            line-height: 1.4;
        }
        .note-highlight {
            color: #D4AF37; /* Złoty kolor nut */
            font-style: normal;
            font-weight: 600;
        }

        .fragrantica-link {
            display: block;
            text-align: right;
            font-size: 11px;
            color: #FFF;
            text-decoration: none;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: 1px solid #333;
            padding: 8px;
            background: #111;
            border-radius: 4px;
        }
        .fragrantica-link:hover {
            background: #222;
            border-color: #D4AF37;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 4. Funkcje pomocnicze (Agresywne czyszczenie) ---
def parse_accords_safe(row_data):
    """Czyści dane, usuwając nawiasy [' '] i zwraca czystą listę."""
    if pd.isna(row_data): return []
    
    # Krok 1: Zamiana na string
    s = str(row_data)
    
    # Krok 2: Jeśli wygląda jak lista Pythona, spróbuj sparsować
    try:
        if s.strip().startswith("["):
            parsed = ast.literal_eval(s)
            if isinstance(parsed, list):
                return [str(i).lower() for i in parsed]
    except:
        pass

    # Krok 3: Jeśli parsowanie zawiodło, użyj siły (Regex)
    # Usuń nawiasy kwadratowe, cudzysłowy pojedyncze i podwójne
    s = re.sub(r"[\[\]'\"/]", "", s)
    
    # Rozdziel po przecinkach i usuń spacje
    return [item.strip().lower() for item in s.split(",") if item.strip()]

# --- 5. Ładowanie Danych ---
@st.cache_data
def load_data(filepath): 
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # Czyszczenie nazwy
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
            
        df['clean_accords'] = df['main_accords'].apply(parse_accords_safe)
        
        all_accords = set()
        for accords_list in df['clean_accords']:
            for note in accords_list:
                all_accords.add(note)
        
        return df, sorted(list(all_accords))
    except Exception:
        return None, []

def render_modular_card(perfume):
    # Wyświetl tylko 5 pierwszych nut, połączone przecinkiem
    notes_list = perfume.clean_accords[:5]
    notes_str = ", ".join(notes_list).upper() if notes_list else "N/A"

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
            MAIN NOTES: <span class="note-highlight">{notes_str}</span>
        </div>
        
        <a href="{perfume.img_link}" target="_blank" class="fragrantica-link">
            View Details on Fragrantica
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 6. Główna Aplikacja ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    
    with st.sidebar:
        st.markdown("### FILTER SEARCH")
        st.write("")
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("**MIN RATING**")
        score = st.slider("min_rating", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("**SCENT NOTES**")
        notes = st.multiselect("scent_notes", unique_accords, placeholder="Select ingredients...", label_visibility="collapsed")
        
        st.markdown("<br><br><div style='color:#666; font-size:10px'>© 2024 Perfume Analytics</div>", unsafe_allow_html=True)

    # Nagłówek
    st.markdown("<h1 style='text-align: center; font-family: Playfair Display; color: #D4AF37; margin-bottom: 0; font-size: 40px;'>PERFUME FINDER</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #888; font-size: 12px; margin-bottom: 40px; letter-spacing: 3px; text-transform: uppercase;'>Data-Driven Fragrance Discovery</div>", unsafe_allow_html=True)

    # Logika filtrowania
    if gender == "All":
        filtered = df.copy()
    else:
        filtered = df[df['gender'] == gender].copy()

    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        def check_notes(row_list):
            return all(note in row_list for note in notes)
        filtered = filtered[filtered['clean_accords'].apply(check_notes)]

    # Wyniki
    st.markdown(f"<div style='color: #FFF; font-size: 14px; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;'>FOUND <b>{len(filtered)}</b> MATCHING PERFUMES</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found matching these criteria. Try lowering the rating or changing gender.")
    else:
        for row in filtered.head(50).itertuples():
            render_modular_card(row)

else:
    st.error("Data Error. Please check fra_perfumes.csv")