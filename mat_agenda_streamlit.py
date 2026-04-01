import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os
from streamlit_calendar import calendar
from supabase import create_client

url = "TON_URL_SUPABASE"
key = "TA_CLE_API"

supabase = create_client(url, key)

DATA_FILE = "agenda_data.csv"

st.set_page_config(
    page_title="MAT AGENDA",
    page_icon="📅",
    layout="wide"
)

# -------------------------
# STYLE CYBERPUNK
# -------------------------

st.markdown("""
<style>
body{
background-color:#0f172a;
color:white;
}

h1{
color:#00ffff;
text-align:center;
}

.stButton>button{
background-color:#ff00ff;
color:white;
border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("📅 MAT AGENDA CYBERPUNK")

# -------------------------
# CHARGER DONNEES
# -------------------------

def charger_donnees():

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["debut"] = pd.to_datetime(df["debut"]).dt.time
            df["fin"] = pd.to_datetime(df["fin"]).dt.time

        return df

    else:
        return pd.DataFrame(columns=["date","debut","fin","description"])

def charger_donnees():

    response = supabase.table("agenda").select("*").execute()

    data = response.data

    return pd.DataFrame(data)

# -------------------------
# AJOUT ACTIVITE
# -------------------------

st.subheader("➕ Ajouter activité")

col1,col2,col3,col4 = st.columns(4)

with col1:
    date = st.date_input("Date")

with col2:
    debut = st.time_input("Début")

with col3:
    fin = st.time_input("Fin")

with col4:
    description = st.text_input("Description")

if st.button("Ajouter activité"):

    supabase.table("agenda").insert({
        "date": str(date),
        "debut": str(debut),
        "fin": str(fin),
        "description": description
    }).execute()

    st.success("Activité ajoutée")

# -------------------------
# CALCUL HEURES
# -------------------------

def calcul_heures(row):

    debut = datetime.datetime.combine(datetime.date.today(), row["debut"])
    fin = datetime.datetime.combine(datetime.date.today(), row["fin"])

    duree = fin - debut

    return duree.total_seconds() / 3600


if not df.empty:

    df["heures"] = df.apply(calcul_heures,axis=1)

# -------------------------
# RECHERCHE
# -------------------------

st.subheader("🔍 Recherche")

recherche = st.text_input("chercher activité")

if recherche:

    res = df[df["description"].astype(str).str.contains(recherche,case=False,na=False)]

    st.dataframe(res)

# -------------------------
# TABLE ACTIVITES
# -------------------------

st.subheader("📋 Activités")

st.dataframe(df)

# -------------------------
# STATISTIQUES
# -------------------------

if not df.empty:

    st.subheader("📊 Statistiques")

    df["mois"] = pd.to_datetime(df["date"]).dt.month

    stats = df.groupby("mois")["heures"].sum().reset_index()

    fig = px.bar(
        stats,
        x="mois",
        y="heures",
        title="Heures par mois"
    )

    st.plotly_chart(fig, use_container_width=True)

    total = df["heures"].sum()

    st.metric("⏱ Total heures", round(total,2))

# -------------------------
# CALENDRIER
# -------------------------

st.subheader("📅 Calendrier")

if not df.empty:

    events = []

    for _, row in df.iterrows():

        events.append({
            "title": str(row["description"]),
            "start": str(row["date"]),
        })

    calendar(events=events)