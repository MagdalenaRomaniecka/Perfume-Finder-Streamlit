import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

# --- 1. KONFIGURACJA (Musi być na samej górze) ---
st.set_page_config(
    page_title="Perfume Finder",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. GOOGLE ANALYTICS (Twoje ID) ---
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

# --- 3. BRUTALNE CZYSZCZENIE DANYCH (Nowe podejście) ---
def brutal_clean(text):
    """Usuwa wszystko co nie jest literą, spacją lub przecinkiem."""
    if pd.isna(text): return []
    # Zamiana na tekst
    text = str(text)
    # Regex: Zostaw tylko a-z, A-Z, przecinki i spacje. Resztę usuń.
    text = re.sub(r"[^a-zA-Z, ]", "", text)
    # Podziel po przecinkach i usuń puste fragmenty
    return [x.strip().upper() for x in text.split(",") if x.strip()]

# --- 4. CSS (Powrót do elegancji) ---
def load_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

        /* Globalne ustawienia */
        html, body, [class*="st-"], [class*="css-"] {
            font-family: 'Montserrat', sans-serif;
            color: #E0E0E0;
            background-color: #0E0E0E; 
        }
        [data-testid="stAppViewContainer"] { background-color: #0E0E0E; }
        [data-testid="stHeader"] { display: none; }

        /* PASEK BOCZNY (Naprawiona wielkość) */
        section[data-testid="stSidebar"] {
            background-color: #111; 
            border-right: 1px solid #333;
        }
        
        /* Nagłówki w pasku bocznym */
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #D4AF37 !important;
            font-family: 'Playfair Display', serif;
            font-size: 16px !important; /* Zmniejszone */
            margin-bottom: 10px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Radio Buttons (Płeć) - Zmniejszone */
        div[role="radiogroup"] label {
            background-color: #161616 !important;
            border: 1px solid #333 !important;
            padding: 8px 12px !important; /* Mniejszy padding */
            border-radius: 4px !important;
            margin-bottom: 5px !important;
        }
        
        div[role="radiogroup"] label p {
            font-size: 13px !important; /* Powrót do 13px */
            color: #AAA !important; 
            font-weight: 500 !important;
        }

        /* Stan zaznaczony */
        div[role="radiogroup"] label:has(input:checked) {
            background-color: #D4AF37 !important;
            border-color: #D4AF37 !important;
        }
        div[role="radiogroup"] label:has(input:checked) p {
            color: #000 !important;
            font-weight: 700 !important;
        }
        div[role="radiogroup"] label div[data-baseweb="radio"] { display: none; }

        /* KARTY PERFUM (Bez zmian, bo są ok) */
        .perfume-container {
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #222;
        }
        .info-row { display: flex; gap: 10px; margin-bottom: 8px; align-items: stretch; }
        
        .box-name {
            flex-grow: 1;
            background-color: #161616;
            border: 1px solid #333;
            border-left: 3px solid #D4AF37;
            padding: 12px;
            border-radius: 4px;
            display: flex; align-items: center;
        }
        .name-text {
            font-family: 'Playfair Display', serif;
            font-size: 16px;
            color: #FFF;
            font-weight: 600;
        }
        .box-rating {
            background-color: #D4AF37; color: #000; min-width: 60px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            border-radius: 4px; padding: 5px;
        }
        .rating-num { font-size: 18px; font-weight: 800; }
        .rating-sub { font-size: 8px; font-weight: 700; }

        .notes-row { font-size: 11px; color: #888; margin-bottom: 8px; }
        .note-highlight { color: #DDD; }

        .fragrantica-link {
            display: inline-block; font-size: 10px; color: #D4AF37;
            text-decoration: none; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
        }
        .fragrantica-link:hover { text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)

# --- 5. ŁADOWANIE DANYCH ---
@st.cache_data
def load_data(filepath): 
    try:
        df = pd.read_csv(filepath)
        # Renaming
        df.rename(columns={'Name': 'name', 'Gender': 'gender', 'Rating Value': 'score', 'Rating Count': 'ratings', 'Main Accords': 'main_accords', 'url': 'img_link'}, inplace=True)
        
        # 1. Naprawa nazw (wycinanie płci z nazwy)
        if 'name' in df.columns and 'gender' in df.columns:
            df['name'] = df.apply(
                lambda row: str(row['name']).replace(str(row['gender']), '').strip() 
                if pd.notna(row['name']) and pd.notna(row['gender']) else row['name'], axis=1
            )
        
        # 2. Mapowanie Płci
        gender_map = {'for women': 'Female', 'for men': 'Male', 'for women and men': 'Unisex'}
        df['gender'] = df['gender'].map(gender_map)
        df.dropna(subset=['main_accords', 'name', 'img_link', 'gender'], inplace=True)
        
        # 3. Naprawa liczb
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
            
        # 4. ZASTOSOWANIE BRUTALNEGO CZYSZCZENIA
        df['clean_accords'] = df['main_accords'].apply(brutal_clean)
        
        # Lista unikalnych nut do filtra
        all_accords = set()
        for accords_list in df['clean_accords']:
            for note in accords_list:
                all_accords.add(note)
        
        return df, sorted(list(all_accords))
    except Exception as e:
        return None, []

# --- 6. RENDEROWANIE KARTY ---
def render_card(perfume):
    # Wybieramy max 5 nut
    notes = perfume.clean_accords[:5]
    # Łączymy je przecinkiem - teraz to czysta lista tekstowa
    notes_str = ", ".join(notes) if notes else "N/A"

    html = f"""
    <div class="perfume-container">
        <div class="info-row">
            <div class="box-name"><div class="name-text">{perfume.name}</div></div>
            <div class="box-rating">
                <div class="rating-num">{perfume.score:.1f}</div>
                <div class="rating-sub">SCORE</div>
            </div>
        </div>
        <div class="notes-row">NOTES: <span class="note-highlight">{notes_str}</span></div>
        <a href="{perfume.img_link}" target="_blank" class="fragrantica-link">FRAGRANTICA ↗</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 7. LOGIKA APLIKACJI ---
load_custom_css()
df, unique_accords = load_data("fra_perfumes.csv")

if df is not None:
    # Sidebar
    with st.sidebar:
        st.markdown("### FILTER SEARCH")
        gender = st.radio("GENDER", ["All", "Female", "Male", "Unisex"], label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### MIN RATING")
        score = st.slider("min_rating", 1.0, 5.0, 4.0, 0.1, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### NOTES")
        notes = st.multiselect("notes", unique_accords, placeholder="Select...", label_visibility="collapsed")
        st.markdown("<br><div style='color:#555; font-size:10px'>© 2024 Ver. Clean</div>", unsafe_allow_html=True)

    # Main
    st.markdown("<h1 style='text-align: center; color: #D4AF37; font-family: Playfair Display;'>PERFUME FINDER</h1>", unsafe_allow_html=True)

    # Filtering
    if gender == "All": filtered = df.copy()
    else: filtered = df[df['gender'] == gender].copy()
    
    filtered = filtered[filtered['score'] >= score]
    
    if notes:
        filtered = filtered[filtered['clean_accords'].apply(lambda x: all(n in x for n in notes))]

    st.markdown(f"<div style='border-bottom:1px solid #333; margin-bottom:20px; padding-bottom:5px; color:#888; font-size:12px'>FOUND {len(filtered)}</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No perfumes found.")
    else:
        for row in filtered.head(50).itertuples():
            render_card(row)
else:
    st.error("Error loading data.")