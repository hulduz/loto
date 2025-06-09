import streamlit as st
import pandas as pd
import datetime
import random
from collections import Counter

st.set_page_config(page_title="EuroMillions Predictor", layout="centered")

st.title("Pronostics EuroMillions")

# 1. Charger les données
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("euromillions_202002.csv", sep=';')  # adapte si besoin
        df['date_de_tirage'] = pd.to_datetime(df['date_de_tirage'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['date_de_tirage'])
        df = df[df['date_de_tirage'] >= (datetime.datetime.now() - datetime.timedelta(days=730))]
        return df
    except Exception as e:
        st.error(f"Erreur chargement CSV: {e}")
        return pd.DataFrame()

df = load_data()

st.write("Données chargées:", df.shape)
if df.empty:
    st.warning("Le dataframe est vide. Vérifie le fichier CSV ou le chemin.")
    st.stop()

# 2. Calcul des fréquences
boules_cols = [f"boule_{i}" for i in range(1, 6)]
etoiles_cols = [f"etoile_{i}" for i in range(1, 3)]

all_boules = pd.concat([df[col] for col in boules_cols], axis=0)
frequencies_boules = Counter(all_boules)
top_boules = [num for num, _ in frequencies_boules.most_common()]

all_etoiles = pd.concat([df[col] for col in etoiles_cols], axis=0)
frequencies_etoiles = Counter(all_etoiles)
top_etoiles = [num for num, _ in frequencies_etoiles.most_common()]

st.write("Top 10 boules principales les plus fréquentes:", top_boules[:10])
st.write("Top 5 étoiles les plus fréquentes:", top_etoiles[:5])

# 3. Méthodes de génération avec protection
def generate_numbers(method='frequent'):
    if len(top_boules) < 20 or len(top_etoiles) < 5:
        st.warning("Pas assez de données pour générer des numéros.")
        return [], [], None

    if method == 'frequent':
        boule_pool = top_boules[:20]
        etoile_pool = top_etoiles[:5]
        if len(boule_pool) < 5 or len(etoile_pool) < 2:
            st.warning("Pas assez de boules ou étoiles fréquentes.")
            return [], [], None
        boules = sorted(random.sample(boule_pool, 5))
        etoiles = sorted(random.sample(etoile_pool, 2))
        return boules, etoiles, None

    elif method == 'rare':
        boule_pool = top_boules[-20:]
        etoile_pool = top_etoiles[-5:]
        if len(boule_pool) < 5 or len(etoile_pool) < 2:
            st.warning("Pas assez de boules ou étoiles rares.")
            return [], [], None
        boules = sorted(random.sample(boule_pool, 5))
        etoiles = sorted(random.sample(etoile_pool, 2))
        return boules, etoiles, None

    elif method == 'mix':
        recent = df.sort_values("date_de_tirage", ascending=False).iloc[0]
        recent_boules = set(recent[boules_cols])
        recent_etoiles = set(recent[etoiles_cols])
        filtered_boules = list(set(top_boules[:25]) - recent_boules)
        filtered_etoiles = list(set(top_etoiles[:10]) - recent_etoiles)

        if len(filtered_boules) < 5 or len(filtered_etoiles) < 2:
            st.warning("Pas assez de boules ou étoiles filtrées pour méthode mixte.")
            return [], [], None
        boules = sorted(random.sample(filtered_boules, 5))
        etoiles = sorted(random.sample(filtered_etoiles, 2))
        return boules, etoiles, None

strategie = st.selectbox("Choisis une stratégie :", ["Fréquence", "Retard", "Mixte"])

if st.button("🎯 Générer"):
    if strategie == "Fréquence":
        boules, etoiles, _ = generate_numbers('frequent')
    elif strategie == "Retard":
        boules, etoiles, _ = generate_numbers('rare')
    else:
        boules, etoiles, _ = generate_numbers('mix')

    if boules and etoiles:
        st.success(f"Numéros proposés : **{boules}** + Étoiles : **{etoiles}**")
    else:
        st.error("Impossible de générer une grille, vérifie les messages précédents.")

with st.expander("📊 Fréquence des boules principales (2 ans)"):
    freq_df_boules = pd.DataFrame.from_dict(frequencies_boules, orient='index', columns=['fréquence']).sort_index()
    st.bar_chart(freq_df_boules)

with st.expander("📊 Fréquence des étoiles (2 ans)"):
    freq_df_etoiles = pd.DataFrame.from_dict(frequencies_etoiles, orient='index', columns=['fréquence']).sort_index()
    st.bar_chart(freq_df_etoiles)

with st.expander("📅 Historique récent des tirages"):
    st.dataframe(df.sort_values("date_de_tirage", ascending=False).reset_index(drop=True), height=300)
