import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

DATA_FILE = "agenda_data.csv"

st.set_page_config(
    page_title="MAT AGENDA",
    page_icon="📅",
    layout="wide"
)

# STYLE CYBERPUNK
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
# Charger données
# -------------------------

def charger_donnees():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["date","debut","fin","description"])

def sauvegarder(df):
    df.to_csv(DATA_FILE,index=False)

df = charger_donnees()

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

    new = pd.DataFrame([{
        "date":date,
        "debut":debut,
        "fin":fin,
        "description":description
    }])

    df = pd.concat([df,new],ignore_index=True)
    sauvegarder(df)

    st.success("Activité ajoutée")

# -------------------------
# CALCUL HEURES
# -------------------------

def calcul_heures(row):

    debut = datetime.datetime.combine(datetime.date.today(),pd.to_datetime(row["debut"]).time())
    fin = datetime.datetime.combine(datetime.date.today(),pd.to_datetime(row["fin"]).time())

    return (fin-debut).seconds/3600

if not df.empty:

    df["heures"] = df.apply(calcul_heures,axis=1)

# -------------------------
# RECHERCHE
# -------------------------

st.subheader("🔍 Recherche")

recherche = st.text_input("chercher activité")

if recherche:

    res = df[df["description"].str.contains(recherche,case=False)]

    st.dataframe(res)

# -------------------------
# TABLE
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

    fig = px.bar(stats,x="mois",y="heures",title="Heures par mois")

    st.plotly_chart(fig)

    total = df["heures"].sum()

    st.metric("⏱ Total heures",round(total,2))

# -------------------------
# CALENDRIER SIMPLE
# -------------------------

st.subheader("📅 Calendrier")

if not df.empty:

    events = []

    for _,row in df.iterrows():

        events.append({
            "title":row["description"],
            "start":row["date"]
        })

    st.write(events)
