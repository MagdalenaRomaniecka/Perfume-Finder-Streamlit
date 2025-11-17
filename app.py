import streamlit as st
import pandas as pd
import plotly.express as px

# --- Konfiguracja strony ---
# Ustawienie strony musi być pierwszą komendą Streamlit
st.set_page_config(
    page_title="Perfume Finder 🔎",
    page_icon="👃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funkcje pomocnicze ---

@st.cache_data
def load_data(filepath):
    """Ładuje dane z pliku CSV i wstępnie je przetwarza."""
    try:
        df = pd.read_csv(filepath)
        # Zmiana nazw kolumn na te używane w kodzie
        df.rename(columns={
            'Nuty Główne': 'main_accords',
            'Nazwa': 'name',
            'Marka': 'brand',
            'Oceny': 'ratings',
            'Ocena': 'score',
            'Płeć': 'gender',
            'Link': 'img_link'
        }, inplace=True)
        
        # Czystka danych: usuwanie wierszy bez kluczowych informacji
        df.dropna(subset=['main_accords', 'name', 'img_link'], inplace=True)
        
        # Konwersja ocen na typ numeryczny (zastępowanie ',' na '.')
        if df['score'].dtype == 'object':
            df['score'] = df['score'].str.replace(',', '.').astype(float)
        
        # Ekstrakcja unikalnych akordów
        all_accords_str = ",".join(df['main_accords'].unique())
        all_accords_list = [accord.strip() for accord in all_accords_str.split(",")]
        unique_accords = sorted(list(set(all_accords_list)))
        
        return df, unique_accords
    except FileNotFoundError:
        st.error(f"Błąd: Nie znaleziono pliku danych pod ścieżką: {filepath}.")
        st.error("Upewnij się, że plik `fra_perfumes.csv` znajduje się w tym samym folderze co `app.py`.")
        st.info("Pobierz plik z: https://www.kaggle.com/datasets/olgagmiufana1/fragrantica-com-fragrance-dataset")
        return None, []
    except Exception as e:
        st.error(f"Wystąpił nieoczekiwany błąd podczas ładowania danych: {e}")
        return None, []

def display_perfume_card(perfume):
    """Wyświetla pojedynczą kartę perfum w galerii."""
    # Użycie `st.container` z ramką dla lepszego efektu wizualnego
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Sprawdzenie, czy link do obrazu istnieje
            if perfume['img_link'] and isinstance(perfume['img_link'], str):
                st.image(perfume['img_link'], use_column_width=True)
            else:
                # Placeholder, jeśli brakuje linku
                st.image("https://placehold.co/200x200/eee/ccc?text=No+Image", use_column_width=True)

        with col2:
            st.markdown(f"**{perfume['name']}**")
            st.markdown(f"*{perfume['brand']}*")
            
            # Formatowanie oceny
            score_str = f"{perfume['score']:.2f}".replace('.', ',')
            st.metric(label="Ocena", value=score_str, delta=f"{perfume['ratings']} ocen")
            
            # Akordy jako tagi
            if perfume['main_accords']:
                accords_list = [f"`{acc.strip()}`" for acc in perfume['main_accords'].split(",")]
                st.markdown("**Akordy:** " + " ".join(accords_list))

# --- Główna aplikacja ---

# Ładowanie danych
df, unique_accords = load_data("fra_perfumes.csv")

# Sprawdzenie, czy dane zostały pomyślnie załadowane
if df is not None:

    # --- Pasek boczny (Sidebar) ---
    with st.sidebar:
        st.image("https://i.imgur.com/Kz81y1S.png", use_column_width=True) # Proste logo/obrazek
        st.title("Filtry Wyszukiwania")

        # Filtr 1: Akordy zapachowe
        selected_accords = st.multiselect(
            "Wybierz główne akordy:",
            options=unique_accords,
            default=["vanilla", "sweet", "powdery"]
        )

        # Filtr 2: Płeć
        gender_options = ["Damskie", "Męskie", "Unisex"]
        selected_gender = st.selectbox(
            "Wybierz płeć:",
            options=gender_options,
            index=0 # Domyślnie "Damskie"
        )

        # Filtr 3: Minimalna ocena
        min_score = st.slider(
            "Minimalna ocena (1.0 - 5.0):",
            min_value=1.0,
            max_value=5.0,
            value=4.0, # Domyślna wartość
            step=0.1
        )
        
        st.markdown("---")
        st.info("Projekt stworzony przez Magdalenę Romaniecką. Dane pochodzą z Kaggle.")

    # --- Główna zawartość strony ---
    
    # Podział na zakładki
    tab1, tab2 = st.tabs(["**🔎 Znajdź Perfumy**", "**📊 Statystyki Rynku**"])

    # --- Zakładka 1: Wyszukiwarka Perfum ---
    with tab1:
        st.title("Inteligentna Wyszukiwarka Perfum")
        st.markdown("Użyj filtrów po lewej stronie, aby znaleźć zapach idealny dla siebie.")

        # Logika filtrowania
        # 1. Filtrowanie wg płci
        filtered_df = df[df['gender'] == selected_gender].copy()

        # 2. Filtrowanie wg oceny
        filtered_df = filtered_df[filtered_df['score'] >= min_score]

        # 3. Filtrowanie wg akordów (muszą być wszystkie wybrane)
        if selected_accords:
            # Tworzymy funkcję pomocniczą, która sprawdza, czy wszystkie akordy z listy 'selected_accords'
            # znajdują się w tekście 'main_accords' danego perfum
            def contains_all_accords(row_accords):
                if pd.isna(row_accords):
                    return False
                # Sprawdzamy każdy akord z listy wybranych
                for accord in selected_accords:
                    if accord not in row_accords:
                        return False
                return True

            # Aplikujemy funkcję do filtrowania
            mask = filtered_df['main_accords'].apply(contains_all_accords)
            filtered_df = filtered_df[mask]

        # Wyświetlanie wyników
        st.markdown("---")
        st.subheader(f"Znaleziono {len(filtered_df)} perfum pasujących do Twoich kryteriów:")

        if filtered_df.empty:
            st.warning("Nie znaleziono żadnych perfum spełniających wszystkie kryteria. Spróbuj złagodzić filtry.")
        else:
            # Wyświetlanie galerii w 3 kolumnach
            num_columns = 3
            cols = st.columns(num_columns)
            
            # Iteracja przez wyniki i wyświetlanie ich w kolumnach
            for index, perfume in enumerate(filtered_df.itertuples()):
                col_index = index % num_columns
                with cols[col_index]:
                    display_perfume_card(perfume)

    # --- Zakładka 2: Statystyki Rynku ---
    with tab2:
        st.title("Statystyki i Trendy Rynkowe")

        # Wykres 1: Rozkład ocen (Histogram)
        st.subheader("Jak rozkładają się oceny perfum?")
        fig_hist = px.histogram(
            df, 
            x="score", 
            nbins=50, 
            title="Histogram ocen wszystkich perfum",
            labels={"score": "Ocena (od 1 do 5)"}
        )
        fig_hist.update_layout(bargap=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)

        # Wykres 2: Najpopularniejsze akordy (Bar chart)
        st.subheader("15 najczęściej występujących akordów zapachowych")
        
        # Zliczanie akordów (wymaga przetworzenia)
        all_accords_flat_list = []
        for accord_string in df['main_accords'].dropna():
            all_accords_flat_list.extend([acc.strip() for acc in accord_string.split(",")])
        
        accords_counts = pd.Series(all_accords_flat_list).value_counts()
        top_15_accords = accords_counts.head(15).sort_values(ascending=True) # Sortowanie rosnąco dla wykresu horyzontalnego

        fig_bar = px.bar(
            top_15_accords,
            x=top_15_accords.values,
            y=top_15_accords.index,
            orientation='h',
            title="Top 15 Akordów w bazie danych",
            labels={"x": "Liczba wystąpień", "y": "Akord"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    # Ten komunikat wyświetli się tylko wtedy, gdy load_data() zwróci None
    st.header("Aplikacja nie może zostać uruchomiona.")
    st.warning("Proszę rozwiązać problem z ładowaniem danych, aby kontynuować.")