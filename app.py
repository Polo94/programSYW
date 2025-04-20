import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
from translations import translations

# Fonction d'initialisation de l'admin
def init_admin():
    admin_username = "admin"
    admin_password = "admin123"
    password_hash = hashlib.sha256(admin_password.encode()).hexdigest()

    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            users = f.readlines()
        admin_exists = any(line.startswith("admin,") for line in users)
        if not admin_exists:
            with open("users.txt", "a") as f:
                f.write(f"{admin_username},{password_hash},True\n")
            print("Compte administrateur créé.")
    else:
        with open("users.txt", "w") as f:
            f.write(f"{admin_username},{password_hash},True\n")
        print("Fichier users.txt créé avec le compte administrateur.")

# Initialisation automatique de l'admin au démarrage
init_admin()

# Configuration de la page
st.set_page_config(page_title="Suivi des Mesures", layout="wide")

#Titre de la page
st.markdown("<h1 style='text-align: center; color: #FF6F61;'>Program SYW</h1>", unsafe_allow_html=True)

# Style CSS personnalisé
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        h1, h2, h3, h4, h5, h6 { color: #FF6F61 !important; }
        .stButton > button {
            background-color: #FF6F61 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
        }
        .stTextInput > div > input,
        .stNumberInput > div > input,
        .stTextArea textarea,
        .stSelectbox > div > div {
            background-color: #E0E0E0 !important;
            color: #222222 !important;
        }
        .stTextInput > label,
        .stNumberInput > label,
        .stTextArea > label,
        .stSelectbox > label,
        .stMarkdown p,
        div[data-baseweb="select"] > div {
            color: #222222 !important;
            font-weight: 500 !important;
        }
        .stDataFrame, .stTable { background-color: #FFFFFF !important; }
        .stSidebar { background-color: #E0E0E0 !important; }
        .stSidebar label,
        .stSidebar .stMarkdown p { color: #222222 !important; font-weight: 500 !important; }
        div[role="radiogroup"] span,
        div[role="radiogroup"] p,
        div[role="radiogroup"] label,
        div[role="radiogroup"] > div {
            color: #222222 !important;
            font-weight: 600 !important;
        }
        .stRadio > label {
            color: #222222 !important;
            font-weight: 600 !important;
        }
        .stAlert, .stAlert p { color: #222222 !important; }
        .stSelectbox label { color: #222222 !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# Sélection de la langue
if 'language' not in st.session_state:
    st.session_state.language = 'fr'

lang = st.sidebar.selectbox(
    "Langue / Language / Idioma",
    options=['fr', 'en', 'es'],
    index=['fr', 'en', 'es'].index(st.session_state.language),
    format_func=lambda x: {'fr': 'Français', 'en': 'English', 'es': 'Español'}[x]
)
st.session_state.language = lang
_ = translations[lang]

# Fonction pour hasher le mot de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentification simple
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Chargement des utilisateurs existants
users = {}
if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
        for line in f:
            username, password_hash, is_admin = line.strip().split(",")
            users[username] = (password_hash, is_admin == "True")

# Formulaire d'inscription
if not st.session_state.authenticated and 'register' not in st.session_state:
    st.title(_["register"])
    new_username = st.text_input(_["new_username"])
    new_password = st.text_input(_["new_password"], type="password")
    confirm_password = st.text_input(_["confirm_password"], type="password")    

    if st.button(_["register_button"]):
        if new_username in users:
            st.error("Ce nom d'utilisateur est déjà pris.")
        elif new_password != confirm_password:
            st.error("Les mots de passe ne correspondent pas.")
        else:
            # Hash du mot de passe
            password_hash = hash_password(new_password)
            # Enregistrement de l'utilisateur
            with open("users.txt", "a") as f:
                f.write(f"{new_username},{password_hash},False\n")
            st.success("Inscription réussie ! Veuillez vous connecter.")
            st.session_state.register = True
            st.rerun()

# Formulaire de connexion
if not st.session_state.authenticated:
    st.title(_["login"])
    username = st.text_input(_["username"])
    password = st.text_input(_["password"], type="password")

    if st.button(_["login_button"]):
        password_hash = hash_password(password)
        if username in users and users[username][0] == password_hash:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.is_admin = users[username][1]
            st.rerun()
        else:
            st.error("Identifiants incorrects")
else:
    # Badge utilisateur
    st.sidebar.markdown(f"""
        <div style='
            padding: 8px 15px;
            border-radius: 5px;
            background-color: #FF6F61;
            color: white;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        '>
            {st.session_state.username}
        </div>
    """, unsafe_allow_html=True)

    # Déconnexion
    if st.sidebar.button(_["logout"]):
        st.session_state.authenticated = False
        st.rerun()

    # Vue admin (pour admin uniquement)
    if st.session_state.get("is_admin", False):
        admin_mode = st.sidebar.checkbox("Vue admin")
    else:
        admin_mode = False

    st.title(_["title"])

    # Mode admin : voir et modifier tous les utilisateurs
    if admin_mode:
        st.header("Vue administrateur : toutes les mesures")
        fichiers = [f for f in os.listdir() if f.startswith("mesures_") and f.endswith(".csv")]
        if not fichiers:
            st.info("Aucune donnée enregistrée pour aucun utilisateur.")
        else:
            utilisateur_selectionne = st.selectbox(
                "Choisir un utilisateur",
                [f.replace("mesures_", "").replace(".csv", "") for f in fichiers]
            )
            csv_file = f"mesures_{utilisateur_selectionne}.csv"
    else:
        # Fichier CSV propre à l'utilisateur connecté
        csv_file = f"mesures_{st.session_state.username}.csv"

    # Sélection entre nouvelle mesure et modification
    if 'action' not in st.session_state:
        st.session_state.action = "Nouvelle mesure"

    action = st.radio(
        "Choisir une action",
        ["Nouvelle mesure", "Modifier une mesure existante"],
        horizontal=True,
        key='action'
    )

    mesure_a_modifier = None
    date_a_modifier = None

    if action == "Modifier une mesure existante":
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                dates_disponibles = df['date'].dt.strftime('%Y-%m-%d').tolist()
                date_a_modifier = st.selectbox(
                    "Sélectionner la date à modifier",
                    dates_disponibles,
                    index=len(dates_disponibles)-1
                )
                mesure_a_modifier = df[df['date'].dt.strftime('%Y-%m-%d') == date_a_modifier].iloc[0]
            else:
                st.warning("Aucune mesure enregistrée à modifier.")
                st.session_state.action = "Nouvelle mesure"
                st.rerun()
        else:
            st.warning("Aucune mesure enregistrée à modifier.")
            st.session_state.action = "Nouvelle mesure"
            st.rerun()

    # Formulaire de saisie ou modification
    st.header(_["add_measure"] if action == "Nouvelle mesure" else "Modifier la mesure")
    with st.form("form_mesure"):
        col1, col2, col3 = st.columns(3)

        with col1:
            if action == "Nouvelle mesure":
                date = st.date_input(_["date"], datetime.now())
            else:
                date = datetime.strptime(date_a_modifier, '%Y-%m-%d')
                st.date_input(_["date"], date, disabled=True)

            taille = st.number_input(_["height"],
                min_value=0.0, max_value=250.0, step=0.1,
                value=float(mesure_a_modifier['taille']) if action == "Modifier une mesure existante" else 0.0)

            poids = st.number_input(_["weight"],
                min_value=0.0, max_value=300.0, step=0.1,
                value=float(mesure_a_modifier['poids']) if action == "Modifier une mesure existante" else 0.0)

        with col2:
            tour_poitrine = st.number_input(_["chest"],
                min_value=0.0, max_value=200.0, step=0.1,
                value=float(mesure_a_modifier['tour_poitrine']) if action == "Modifier une mesure existante" else 0.0)

            tour_taille = st.number_input(_["waist"],
                min_value=0.0, max_value=200.0, step=0.1,
                value=float(mesure_a_modifier['tour_taille']) if action == "Modifier une mesure existante" else 0.0)

            tour_hanches = st.number_input(_["hips"],
                min_value=0.0, max_value=200.0, step=0.1,
                value=float(mesure_a_modifier['tour_hanches']) if action == "Modifier une mesure existante" else 0.0)

        with col3:
            tour_bras = st.number_input(_["arm"],
                min_value=0.0, max_value=100.0, step=0.1,
                value=float(mesure_a_modifier['tour_bras']) if action == "Modifier une mesure existante" else 0.0)

            tour_cuisse = st.number_input(_["thigh"],
                min_value=0.0, max_value=100.0, step=0.1,
                value=float(mesure_a_modifier['tour_cuisse']) if action == "Modifier une mesure existante" else 0.0)

            tour_epaule = st.number_input(_["shoulder"],
                min_value=0.0, max_value=200.0, step=0.1,
                value=float(mesure_a_modifier['tour_epaule']) if action == "Modifier une mesure existante" else 0.0)

        masse_grasse = st.number_input(_["fat"],
            min_value=0.0, max_value=100.0, step=0.1,
            value=float(mesure_a_modifier['masse_grasse']) if action == "Modifier une mesure existante" else 0.0)

        remarques = st.text_area(_["remarks"],
            value=mesure_a_modifier['remarques'] if action == "Modifier une mesure existante" else "")

        submit = st.form_submit_button("Modifier" if action == "Modifier une mesure existante" else _["save"])

        if submit:
            new_row = pd.DataFrame([{
                "date": date.strftime("%Y-%m-%d"),
                "taille": taille,
                "poids": poids,
                "tour_poitrine": tour_poitrine,
                "tour_taille": tour_taille,
                "tour_hanches": tour_hanches,
                "tour_bras": tour_bras,
                "tour_cuisse": tour_cuisse,
                "tour_epaule": tour_epaule,
                "masse_grasse": masse_grasse,
                "remarques": remarques
            }])

            if action == "Modifier une mesure existante":
                df = df[df['date'].dt.strftime('%Y-%m-%d') != date_a_modifier]
                df = pd.concat([df, new_row], ignore_index=True)
                st.success("Mesure modifiée avec succès!")
            else:
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    df = pd.concat([df, new_row], ignore_index=True)
                else:
                    df = new_row
                st.success(_["measure_saved"])

            df.to_csv(csv_file, index=False)

    # Affichage des mesures enregistrées et graphiques
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        st.subheader(_["detailed_table"] if "detailed_table" in _ else "Tableau des mesures")
        st.dataframe(df)

        if not df.empty:
            st.subheader(_["weight_evolution"] if "weight_evolution" in _ else "Évolution du poids")
            st.line_chart(df.set_index("date")["poids"])

            if "taille" in df.columns and "poids" in df.columns:
                df["imc"] = df.apply(lambda row: row["poids"] / ((row["taille"]/100)**2) if row["taille"] > 0 else None, axis=1)
                st.subheader(_["bmi_evolution"] if "bmi_evolution" in _ else "Évolution de l'IMC")
                st.line_chart(df.set_index("date")["imc"])

            if "masse_grasse" in df.columns:
                st.subheader(_["fat_evolution"] if "fat_evolution" in _ else "Évolution de la masse grasse")
                st.line_chart(df.set_index("date")["masse_grasse"])