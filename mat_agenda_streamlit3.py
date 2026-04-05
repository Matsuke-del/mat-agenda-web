import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_calendar import calendar

FILE = "agenda.txt"

st.set_page_config(layout="wide")
st.title("🧠 MAT AGENDA TXT")

# =========================
# STYLE
# =========================

st.markdown("""
<style>
.stApp{background:#0b0f14;color:#00ff9c;}
h1,h2,h3{color:#00ffee;}
.stButton>button{background:#00ff9c;color:black;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# =========================
# CREER FICHIER
# =========================

if not os.path.exists(FILE):
    open(FILE,"w").close()

# =========================
# LECTURE TXT
# =========================

def lire_data():

    data=[]

    with open(FILE,"r",encoding="utf-8") as f:

        for line in f:

            parts=line.strip().split("|")

            if len(parts)==6:

                data.append({
                    "id":int(parts[0]),
                    "date":parts[1],
                    "debut":parts[2],
                    "fin":parts[3],
                    "description":parts[4],
                    "color":parts[5]
                })

    return pd.DataFrame(data)

df=lire_data()

# =========================
# NAVIGATION
# =========================

page=st.sidebar.radio(
"Navigation",
["📅 Calendrier","📂 Liste","📊 Statistiques"]
)

# =========================
# AJOUT ACTIVITE
# =========================

st.sidebar.header("➕ Ajouter activité")

date=st.sidebar.date_input("Date")
debut=st.sidebar.time_input("Début")
fin=st.sidebar.time_input("Fin")

desc=st.sidebar.text_area("Description")
color=st.sidebar.color_picker("Couleur","#00ff9c")

if st.sidebar.button("Ajouter activité"):

    if desc.strip()=="":

        st.sidebar.warning("Description obligatoire")

    else:

        desc=desc.replace("|"," ")  # éviter bug format

        new_id=1
        if not df.empty:
            new_id=int(df["id"].max())+1

        ligne=f"{new_id}|{date}|{debut.strftime('%H:%M:%S')}|{fin.strftime('%H:%M:%S')}|{desc}|{color}\n"

        with open(FILE,"a",encoding="utf-8") as f:
            f.write(ligne)

        st.success("Activité ajoutée")

        st.rerun()

# =========================
# TRI
# =========================

if not df.empty:
    df=df.sort_values(["date","debut"])

# =========================
# CALCUL HEURES
# =========================

def calc_heures(row):

    try:
        d=datetime.strptime(row["debut"],"%H:%M:%S")
        f=datetime.strptime(row["fin"],"%H:%M:%S")

        return (f-d).seconds/3600
    except:
        return 0

if not df.empty:
    df["heures"]=df.apply(calc_heures,axis=1)

# =========================
# RECHERCHE
# =========================

search=st.sidebar.text_input("🔎 Recherche")

if search!="" and not df.empty:
    df=df[df["description"].str.contains(search,case=False)]

# =========================
# CALENDRIER
# =========================

if page=="📅 Calendrier":

    st.header("📅 Calendrier")

    if not df.empty:

        events=[]

        for _,row in df.iterrows():

            events.append({
                "title":row["description"],
                "start":row["date"]+"T"+row["debut"],
                "end":row["date"]+"T"+row["fin"],
                "color":row["color"]
            })

        calendar(events=events)

    else:
        st.info("Aucune activité")

# =========================
# LISTE
# =========================

if page=="📂 Liste":

    st.header("📂 Activités")

    if df.empty:
        st.info("Aucune activité")

    else:

        for _,row in df.iterrows():

            col1,col2=st.columns([6,1])

            with col1:

                st.markdown(f"""
### {row['description']}

📅 {row['date']}

⏰ {row['debut']} → {row['fin']}

⏱ {round(row['heures'],2)} h
""")

            with col2:

                if st.button("❌",key=row["id"]):

                    lignes=[]

                    with open(FILE,"r",encoding="utf-8") as f:

                        for line in f:

                            if not line.startswith(str(row["id"])+"|"):
                                lignes.append(line)

                    with open(FILE,"w",encoding="utf-8") as f:
                        f.writelines(lignes)

                    st.rerun()

# =========================
# STATISTIQUES
# =========================

if page=="📊 Statistiques":

    st.header("📊 Statistiques")

    if df.empty:

        st.info("Pas de données")

    else:

        col1,col2=st.columns(2)

        with col1:
            st.metric("⏱ Temps total",f"{round(df['heures'].sum(),2)} h")

        with col2:
            st.metric("📅 Activités",len(df))

        df["mois"]=pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

        stats=df.groupby("mois")["heures"].sum()

        st.subheader("Heures par mois")

        st.bar_chart(stats)