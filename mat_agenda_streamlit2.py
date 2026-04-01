import streamlit as st
from datetime import datetime
import os
import pandas as pd

FILE = "agenda.txt"

# =========================
# STYLE CYBERPUNK
# =========================

st.markdown("""
<style>
body {
background-color:#0b0f14;
color:#00ff9c;
}

h1,h2,h3 {
color:#00ffea;
}

.stButton>button {
background-color:#111;
color:#00ffea;
border:1px solid #00ffea;
}

.stTextInput>div>div>input {
background-color:#111;
color:#00ffea;
}

</style>
""",unsafe_allow_html=True)

st.title("🧠 MAT AGENDA CYBER")

# =========================
# LECTURE FICHIER
# =========================

def lire_activites():

    if not os.path.exists(FILE):
        return []

    data=[]

    with open(FILE,"r",encoding="utf-8") as f:

        for ligne in f:

            ligne=ligne.strip()

            if ligne=="": 
                continue

            parts=ligne.split("|",3)

            if len(parts)==4:

                date,debut,fin,desc=parts

                data.append((date,debut,fin,desc))

    return data


# =========================
# AJOUT ACTIVITE
# =========================

def ajouter(date,debut,fin,desc):

    with open(FILE,"a",encoding="utf-8") as f:

        f.write(f"{date}|{debut}|{fin}|{desc}\n")


# =========================
# CALCUL HEURES
# =========================

def calc_heures(debut,fin):

    d=datetime.strptime(debut,"%H:%M")

    f=datetime.strptime(fin,"%H:%M")

    return (f-d).seconds/3600


# =========================
# FORMULAIRE AJOUT
# =========================

st.header("➕ Ajouter activité")

date = st.date_input("Date")

debut = st.text_input("Heure début","08:00")

fin = st.text_input("Heure fin","15:00")

desc = st.text_area("Description")

if st.button("Ajouter activité"):

    date_str=date.strftime("%d/%m/%Y")

    if desc.strip()!="":

        ajouter(date_str,debut,fin,desc)

        st.success("Activité enregistrée")


# =========================
# LECTURE DATA
# =========================

activites=lire_activites()

data=[]

for d,deb,fin,desc in activites:

    heures=calc_heures(deb,fin)

    mois=datetime.strptime(d,"%d/%m/%Y").strftime("%Y-%m")

    data.append({
    "date":d,
    "debut":deb,
    "fin":fin,
    "description":desc,
    "heures":heures,
    "mois":mois
    })

df=pd.DataFrame(data)

# =========================
# RECHERCHE
# =========================

st.header("🔍 Recherche activité")

search=st.text_input("Mot clé")

if search!="":

    df=df[df["description"].str.contains(search,case=False)]

# =========================
# AFFICHAGE ACTIVITES
# =========================

st.header("📂 Activités")

for index,row in df.iterrows():

    st.markdown(f"""
**{row['date']} | {row['debut']} - {row['fin']}**

{row['description']}

---
""")

# =========================
# HEURES MENSUELLES
# =========================

if not df.empty:

    st.header("⏱ Heures mensuelles")

    heures_mois=df.groupby("mois")["heures"].sum()

    for mois,h in heures_mois.items():

        st.write(f"{mois} : {round(h,1)} H")


# =========================
# GRAPHIQUE
# =========================

if not df.empty:

    st.header("📊 Graphique des heures")

    st.bar_chart(heures_mois)