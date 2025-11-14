# 🔎 Perfume Finder: Intelligent Fragrance Search Engine

## Project Goal

The **Perfume Finder** project is an interactive web application built using Streamlit and the Pandas library. Its purpose is to explore and filter a vast collection of perfumery data, enabling users to quickly find perfumes matched to their preferences based on main fragrance accords, gender, and rating score.

## Data Source

The application uses data downloaded from Kaggle—a dataset sourced from Fragrantica.com (specifically the `fra_perfumes.csv` file).

## Key Features

1. **Advanced Filtering:** Filter perfumes based on selected accords (e.g., "vanilla", "woody", "citrus"), gender, and a minimum user rating.

2. **Results Gallery:** Display matching perfumes in a dynamic gallery format with images and key information.

3. **Market Insights:** A second tab provides visual analysis of market trends, such as rating distribution and the most popular fragrance accords using Plotly.

## 🚀 Getting Started: Running the App Locally

Follow these simple steps to get the Perfume Finder running on your own computer.

### Step 1: Prerequisites (What You Need)

Before you begin, make sure you have the following installed:
* **Python:** Version 3.9 or newer is recommended.
* **Git:** (Optional, but good for downloading from GitHub).

### Step 2: Download the Project & Data

1.  **Clone the repository** (lub pobierz plik ZIP z GitHuba):
    ```bash
    git clone [https://github.com/MagdalenaRomaniecka/Perfume-Finder-Streamlit.git](https://github.com/MagdalenaRomaniecka/Perfume-Finder-Streamlit.git)
    ```
2.  **Navigate into the project folder:**
    ```bash
    cd Perfume-Finder-Streamlit
    ```
3.  **Add your data file:** Download the `fra_perfumes.csv` file from the [Kaggle Dataset](https://www.kaggle.com/datasets/olgagmiufana1/fragrantica-com-fragrance-dataset) and place it **inside** the `Perfume-Finder-Streamlit` folder.

    Your folder must look like this:
    ```
    Perfume-Finder-Streamlit/
    ├── app.py
    ├── fra_perfumes.csv   <-- IMPORTANT!
    ├── requirements.txt
    └── README.md
    ```

### Step 3: Install Dependencies

While in the project folder, install all required libraries with this command:

```bash
pip install -r requirements.txt
streamlit run app.py
## Acknowledgements

This project utilizes an open dataset created by Olga Gmiufana.

 **Dataset:** Fragrantica.com Fragrance Dataset
 **Author:** Olga Gmiufana
 **Kaggle Source:** https://www.kaggle.com/datasets/olgagmiufana1/fragrantica-com-fragrance-dataset

