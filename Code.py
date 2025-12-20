import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import json
import base64
from io import BytesIO
import hashlib
import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict
import time

# Configuration de la page
st.set_page_config(
    page_title="École Ivoirienne - Gestion Scolaire",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# STYLE CSS - Charte graphique
# ============================================

st.markdown("""
<style>
    :root {
        --primary-100: #d4eaf7;
        --primary-200: #b6ccd8;
        --primary-300: #3b3c3d;
        --accent-100: #71c4ef;
        --accent-200: #00668c;
        --text-100: #1d1c1c;
        --text-200: #313d44;
        --background-100: #fffefb;
        --background-200: #f5f4f1;
        --background-300: #cccbc8;
    }
    
    .main {
        background-color: var(--background-100);
    }
    
    .stApp {
        background-color: var(--background-100);
    }
    
    h1, h2, h3, h4 {
        color: var(--primary-300) !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .css-1d391kg {
        background-color: var(--background-100);
    }
    
    .stButton > button {
        background-color: var(--accent-100);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 4px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: var(--accent-200);
        color: white;
    }
    
    .card {
        background-color: var(--background-200);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid var(--accent-100);
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar .sidebar-content {
        background-color: var(--background-200);
    }
    
    .header-container {
        background: linear-gradient(135deg, var(--accent-100), var(--accent-200));
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    
    .info-message {
        background-color: var(--primary-100);
        color: var(--primary-300);
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid var(--primary-200);
        margin: 1rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-top: 4px solid var(--accent-100);
    }
    
    .subject-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: var(--accent-100);
        color: white;
        border-radius: 15px;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CLASSES ET DONNÉES SIMULÉES
# ============================================

@dataclass
class User:
    username: str
    password_hash: str
    role: str  # 'parent', 'enseignant', 'admin'
    nom: str
    prenom: str
    email: str
    telephone: str
    
@dataclass
class Eleve:
    id: int
    nom: str
    prenom: str
    classe: str  # '6ème A', 'Terminale D', etc.
    date_naissance: str
    parent_id: str
    
@dataclass
class Note:
    id: int
    eleve_id: int
    matiere: str
    note: float
    coefficient: int
    type_note: str  # 'Devoir', 'Composition', 'Oral'
    date: str
    enseignant: str
    
@dataclass
class Activite:
    id: int
    titre: str
    description: str
    type_activite: str  # 'Sortie', 'Culturelle', 'Sportive', 'Pédagogique'
    date: str
    heure: str
    lieu: str
    organisateur: str
    classes_concernées: List[str]

class SchoolManagementSystem:
    def __init__(self):
        self.users = {}
        self.eleves = []
        self.notes = []
        self.activites = []
        self.emplois_du_temps = {}
        self.init_demo_data()
        
    def init_demo_data(self):
        # Données de démonstration pour une école ivoirienne
        ivoirien_noms = ['Kouamé', 'Koné', 'Yao', 'Touré', 'Diaby', 
                        'Cissé', 'Bamba', 'Koffi', 'Soro', 'Doumbia']
        ivoirien_prenoms = ['Aya', 'Moussa', 'Fatou', 'Jean', 'Marie',
                           'Paul', 'Aminata', 'Mohamed', 'Rokia', 'Sékou']
        
        # Classes typiques ivoiriennes
        classes = [
            '6ème A', '6ème B',
            '5ème A', '5ème B',
            '4ème A', '4ème B',
            '3ème A', '3ème B',
            'Seconde A', 'Seconde C',
            'Première A', 'Première D',
            'Terminale A', 'Terminale D'
        ]
        
        # Matières selon le système ivoirien
        self.matieres = {
            '6ème-5ème': ['Mathématiques', 'Français', 'Anglais', 'Histoire-Géo', 'SVT', 'EPS'],
            '4ème-3ème': ['Mathématiques', 'Français', 'Anglais', 'Histoire-Géo', 'SVT', 'Physique-Chimie', 'EPS'],
            'Lycée': ['Mathématiques', 'Philosophie', 'Français', 'Anglais', 'Histoire-Géo', 
                     'SVT', 'Physique-Chimie', 'EPS', 'Spécialité']
        }
        
        # Création d'élèves
        for i in range(1, 31):
            nom = random.choice(ivoirien_noms)
            prenom = random.choice(ivoirien_prenoms)
            classe = random.choice(classes)
            eleve = Eleve(
                id=i,
                nom=nom,
                prenom=prenom,
                classe=classe,
                date_naissance=f"{random.randint(2004, 2012)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                parent_id=f"parent_{i%5+1}"
            )
            self.eleves.append(eleve)
            
            # Création de notes pour chaque élève
            matieres_eleve = self.get_matieres_by_classe(classe)
            for matiere in matieres_eleve:
                for _ in range(3):  # 3 notes par matière
                    note = Note(
                        id=len(self.notes)+1,
                        eleve_id=i,
                        matiere=matiere,
                        note=random.uniform(8, 19),
                        coefficient=random.choice([1, 2, 3]),
                        type_note=random.choice(['Devoir', 'Composition', 'Oral']),
                        date=f"2024-{random.randint(1,6):02d}-{random.randint(1,28):02d}",
                        enseignant=f"Prof. {random.choice(['Koné', 'Traoré', 'Yao', 'Cissé'])}"
                    )
                    self.notes.append(note)
        
        # Création d'activités
        activites_ecole = [
            ("Sortie au Musée des Civilisations", "Visite culturelle", "Culturelle", "2024-04-15", "09:00", "Musée, Plateau"),
            ("Tournoi de football inter-classes", "Compétition sportive", "Sportive", "2024-04-20", "14:00", "Stade municipal"),
            ("Journée portes ouvertes", "Présentation des filières", "Pédagogique", "2024-05-10", "08:30", "École"),
            ("Séminaire d'orientation", "Orientation après le BAC", "Pédagogique", "2024-05-25", "10:00", "Salle polyvalente"),
            ("Fête de fin d'année", "Spectacle et remise des prix", "Culturelle", "2024-06-30", "16:00", "Cour de l'école")
        ]
        
        for i, (titre, desc, type_a, date, heure, lieu) in enumerate(activites_ecole):
            activite = Activite(
                id=i+1,
                titre=titre,
                description=desc,
                type_activite=type_a,
                date=date,
                heure=heure,
                lieu=lieu,
                organisateur="Direction de l'école",
                classes_concernées=random.sample(classes, 5)
            )
            self.activites.append(activite)
        
        # Création d'utilisateurs de démonstration
        demo_users = [
            User("parent1", self.hash_password("pass123"), "parent", "Kouamé", "Aminata", "parent1@example.ci", "07 12 34 56 78"),
            User("prof1", self.hash_password("prof123"), "enseignant", "Yao", "Koffi", "prof1@ecole.ci", "05 23 45 67 89"),
            User("admin", self.hash_password("admin123"), "admin", "Admin", "System", "admin@ecole.ci", "01 23 45 67 89"),
        ]
        
        for user in demo_users:
            self.users[user.username] = user
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_matieres_by_classe(self, classe):
        if "6ème" in classe or "5ème" in classe:
            return self.matieres['6ème-5ème']
        elif "4ème" in classe or "3ème" in classe:
            return self.matieres['4ème-3ème']
        else:
            return self.matieres['Lycée']
    
    def get_eleves_by_parent(self, parent_id):
        return [e for e in self.eleves if e.parent_id == parent_id]
    
    def get_notes_by_eleve(self, eleve_id):
        return [n for n in self.notes if n.eleve_id == eleve_id]
    
    def get_moyenne_by_eleve(self, eleve_id):
        notes_eleve = self.get_notes_by_eleve(eleve_id)
        if not notes_eleve:
            return 0
        
        total_pondere = sum(n.note * n.coefficient for n in notes_eleve)
        total_coeff = sum(n.coefficient for n in notes_eleve)
        
        return round(total_pondere / total_coeff, 2) if total_coeff > 0 else 0
    
    def get_moyenne_by_matiere(self, eleve_id, matiere):
        notes_matiere = [n for n in self.notes if n.eleve_id == eleve_id and n.matiere == matiere]
        if not notes_matiere:
            return 0
        
        total_pondere = sum(n.note * n.coefficient for n in notes_matiere)
        total_coeff = sum(n.coefficient for n in notes_matiere)
        
        return round(total_pondere / total_coeff, 2) if total_coeff > 0 else 0

# ============================================
# INITIALISATION DE L'APPLICATION
# ============================================

if 'system' not in st.session_state:
    st.session_state.system = SchoolManagementSystem()
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.selected_eleve = None

system = st.session_state.system

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def display_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="header-container">
            <h1>🏫 École Excellence Ivoirienne</h1>
            <h3>De la 6ème à la Terminale - Système de Gestion Scolaire</h3>
            <p>Plateforme officielle de suivi scolaire - Abidjan, Côte d'Ivoire</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.logged_in:
            user = st.session_state.current_user
            st.info(f"👤 Connecté en tant que: {user.prenom} {user.nom}")
            if st.button("Déconnexion"):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.rerun()

def login_form():
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h2>🔐 Connexion à la plateforme</h2>
        <p>Accédez aux informations scolaires de vos enfants</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            
            if st.button("Se connecter", type="primary", use_container_width=True):
                if username in system.users:
                    user = system.users[username]
                    if user.password_hash == system.hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.current_user = user
                        st.success(f"Connexion réussie ! Bienvenue {user.prenom} {user.nom}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Mot de passe incorrect")
                else:
                    st.error("Utilisateur non trouvé")
            
            st.markdown("---")
            st.markdown("""
            <div class='info-message'>
                <h4>🔑 Identifiants de démonstration</h4>
                <p><strong>Parent :</strong> parent1 / pass123</p>
                <p><strong>Enseignant :</strong> prof1 / prof123</p>
                <p><strong>Administrateur :</strong> admin / admin123</p>
            </div>
            """, unsafe_allow_html=True)

def parent_dashboard():
    user = st.session_state.current_user
    
    # Titre du tableau de bord
    st.markdown(f"""
    <div style='margin-bottom: 2rem;'>
        <h2>👨‍👩‍👧‍👦 Tableau de bord Parent - {user.prenom} {user.nom}</h2>
        <p>Suivez la scolarité de vos enfants</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupérer les élèves associés au parent
    eleves_parent = system.get_eleves_by_parent(user.username)
    
    if not eleves_parent:
        st.warning("Aucun élève n'est associé à votre compte.")
        return
    
    # Sélection de l'élève à afficher
    eleve_options = {f"{e.prenom} {e.nom} - {e.classe}": e for e in eleves_parent}
    selected_eleve_name = st.selectbox(
        "Sélectionnez un élève :",
        list(eleve_options.keys())
    )
    
    selected_eleve = eleve_options[selected_eleve_name]
    st.session_state.selected_eleve = selected_eleve
    
    # Statistiques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        notes_eleve = system.get_notes_by_eleve(selected_eleve.id)
        moyenne = system.get_moyenne_by_eleve(selected_eleve.id)
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{moyenne}/20</h3>
            <p>Moyenne générale</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{len(notes_eleve)}</h3>
            <p>Notes enregistrées</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{selected_eleve.classe}</h3>
            <p>Classe</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Calcul de la position (simulation)
        position = random.randint(1, 35)
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{position}e/{position+20}</h3>
            <p>Rang dans la classe</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Onglets pour les différentes fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Notes et résultats", "📅 Emploi du temps", "📢 Activités scolaires", "📋 Informations"])
    
    with tab1:
        display_notes_tab(selected_eleve)
    
    with tab2:
        display_emploi_du_temps(selected_eleve)
    
    with tab3:
        display_activites_scolaires()
    
    with tab4:
        display_informations_eleve(selected_eleve)

def display_notes_tab(eleve):
    st.markdown(f"### 📊 Notes de {eleve.prenom} {eleve.nom} - {eleve.classe}")
    
    # Graphique des moyennes par matière
    matieres = system.get_matieres_by_classe(eleve.classe)
    moyennes_matieres = []
    
    for matiere in matieres:
        moyenne = system.get_moyenne_by_matiere(eleve.id, matiere)
        moyennes_matieres.append({
            'matiere': matiere,
            'moyenne': moyenne
        })
    
    df_moyennes = pd.DataFrame(moyennes_matieres)
    
    if not df_moyennes.empty:
        fig = px.bar(df_moyennes, x='matiere', y='moyenne',
                    title=f'Moyennes par matière - {eleve.classe}',
                    color='moyenne',
                    color_continuous_scale='Blues',
                    range_y=[0, 20])
        st.plotly_chart(fig, use_container_width=True)
    
    # Détail des notes
    st.markdown("### Détail des notes")
    notes_eleve = system.get_notes_by_eleve(eleve.id)
    
    if notes_eleve:
        notes_data = []
        for note in notes_eleve:
            notes_data.append({
                'Matière': note.matiere,
                'Note': note.note,
                'Coefficient': note.coefficient,
                'Type': note.type_note,
                'Date': note.date,
                'Enseignant': note.enseignant
            })
        
        df_notes = pd.DataFrame(notes_data)
        df_notes = df_notes.sort_values('Date', ascending=False)
        
        # Grouper par matière
        for matiere in df_notes['Matière'].unique():
            with st.expander(f"📚 {matiere}"):
                df_matiere = df_notes[df_notes['Matière'] == matiere]
                st.dataframe(df_matiere, use_container_width=True)
                
                # Calcul moyenne de la matière
                if not df_matiere.empty:
                    moyenne_matiere = system.get_moyenne_by_matiere(eleve.id, matiere)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"Moyenne {matiere}", f"{moyenne_matiere}/20")
                    with col2:
                        appreciation = "Excellent" if moyenne_matiere >= 16 else \
                                     "Très bien" if moyenne_matiere >= 14 else \
                                     "Bien" if moyenne_matiere >= 12 else \
                                     "Assez bien" if moyenne_matiere >= 10 else \
                                     "Passable" if moyenne_matiere >= 8 else "Insuffisant"
                        st.metric("Appréciation", appreciation)
        
        # Téléchargement du bulletin (simulé)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Générer le bulletin PDF", use_container_width=True):
                st.success("Bulletin généré avec succès ! (Fonctionnalité de démonstration)")
        with col2:
            if st.button("📊 Voir l'évolution", use_container_width=True):
                st.info("Fonctionnalité d'évolution temporelle en développement")
    else:
        st.info(f"Aucune note disponible pour {eleve.prenom} {eleve.nom}")

def display_emploi_du_temps(eleve):
    st.markdown(f"### 📅 Emploi du temps - {eleve.classe}")
    
    # Emploi du temps simulé pour une école ivoirienne
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    creneaux = ["8h-10h", "10h-12h", "Pause", "14h-16h", "16h-18h"]
    
    # Matières selon la classe
    matieres = system.get_matieres_by_classe(eleve.classe)
    
    # Génération d'un emploi du temps aléatoire mais cohérent
    emploi_data = []
    for jour in jours:
        if jour == "Samedi":  # Demi-journée le samedi
            jour_creneaux = creneaux[:2]
        else:
            jour_creneaux = creneaux
        
        for creneau in jour_creneaux:
            if creneau != "Pause":
                if "6ème" in eleve.classe or "5ème" in eleve.classe:
                    matiere = random.choice(matieres)
                    salle = f"Salle {random.randint(1, 20)}"
                    prof = f"Prof. {random.choice(['Koné', 'Traoré', 'Yao'])}"
                elif "4ème" in eleve.classe or "3ème" in eleve.classe:
                    matiere = random.choice(matieres)
                    salle = f"Labo {random.choice(['A', 'B', 'C'])}" if matiere in ['SVT', 'Physique-Chimie'] else f"Salle {random.randint(20, 30)}"
                    prof = f"Prof. {random.choice(['Cissé', 'Bamba', 'Diaby'])}"
                else:  # Lycée
                    matiere = random.choice(matieres)
                    salle = f"Amphi {random.randint(1, 3)}" if matiere == "Philosophie" else f"Salle {random.randint(30, 40)}"
                    prof = f"Prof. {random.choice(['Yao', 'Touré', 'Kouamé'])}"
                
                emploi_data.append({
                    'Jour': jour,
                    'Créneau': creneau,
                    'Matière': matiere,
                    'Enseignant': prof,
                    'Salle': salle
                })
    
    df_emploi = pd.DataFrame(emploi_data)
    
    # Affichage sous forme de tableau
    st.dataframe(
        df_emploi,
        column_config={
            "Jour": st.column_config.TextColumn("Jour"),
            "Créneau": st.column_config.TextColumn("Horaire"),
            "Matière": st.column_config.TextColumn("Matière"),
            "Enseignant": st.column_config.TextColumn("Professeur"),
            "Salle": st.column_config.TextColumn("Salle")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Légende
    st.markdown("""
    <div class='info-message'>
        <p><strong>Note :</strong> L'emploi du temps est actualisé chaque semaine. 
        Les modifications sont notifiées par SMS aux parents.</p>
    </div>
    """, unsafe_allow_html=True)

def display_activites_scolaires():
    st.markdown("### 📢 Activités et Événements de l'École")
    
    # Filtrer les activités à venir
    activites_a_venir = [a for a in system.activites if a.date >= "2024-04-01"]
    
    if not activites_a_venir:
        st.info("Aucune activité à venir pour le moment.")
        return
    
    for activite in activites_a_venir:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class='card'>
                    <h4>{activite.titre}</h4>
                    <p><strong>📅 Date :</strong> {activite.date} à {activite.heure}</p>
                    <p><strong>📍 Lieu :</strong> {activite.lieu}</p>
                    <p><strong>📋 Description :</strong> {activite.description}</p>
                    <p><strong>👥 Classes concernées :</strong> {', '.join(activite.classes_concernées[:3])}...</p>
                    <span class='subject-badge'>{activite.type_activite}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("S'inscrire", key=f"inscrire_{activite.id}"):
                    st.success(f"Inscription enregistrée pour {activite.titre}")

def display_informations_eleve(eleve):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='card'>
            <h4>👤 Informations personnelles</h4>
            <p><strong>Nom complet :</strong> {eleve.prenom} {eleve.nom}</p>
            <p><strong>Classe :</strong> {eleve.classe}</p>
            <p><strong>Date de naissance :</strong> {eleve.date_naissance}</p>
            <p><strong>Année scolaire :</strong> 2023-2024</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card'>
            <h4>📚 Matières étudiées</h4>
            <div style='margin-top: 1rem;'>
        """, unsafe_allow_html=True)
        
        matieres = system.get_matieres_by_classe(eleve.classe)
        for matiere in matieres:
            st.markdown(f'<span class="subject-badge">{matiere}</span>', unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h4>🏫 Informations administratives</h4>
            <p><strong>Établissement :</strong> École Excellence Ivoirienne</p>
            <p><strong>Adresse :</strong> Rue des Écoles, Cocody, Abidjan</p>
            <p><strong>Téléphone :</strong> 27 22 40 00 00</p>
            <p><strong>Email :</strong> contact@excellence-ecole.ci</p>
            <p><strong>Directeur :</strong> Dr. Paul Yao</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card'>
            <h4>📞 Contacts d'urgence</h4>
            <p><strong>Infirmerie scolaire :</strong> 27 22 40 00 01</p>
            <p><strong>Vie scolaire :</strong> 27 22 40 00 02</p>
            <p><strong>Conseiller d'orientation :</strong> 27 22 40 00 03</p>
            <p><strong>Urgences :</strong> 111 ou 185</p>
        </div>
        """, unsafe_allow_html=True)

def teacher_dashboard():
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h2>👨‍🏫 Tableau de bord Enseignant</h2>
        <p>Gestion des notes et suivi des élèves</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Saisie des notes", "👥 Gestion des classes", "📊 Statistiques"])
    
    with tab1:
        st.markdown("### Saisie des notes")
        
        # Sélection de la classe
        classes = sorted(list(set([e.classe for e in system.eleves])))
        selected_classe = st.selectbox("Sélectionnez une classe :", classes)
        
        # Sélection de la matière
        matieres = system.get_matieres_by_classe(selected_classe)
        selected_matiere = st.selectbox("Sélectionnez une matière :", matieres)
        
        # Liste des élèves de la classe
        eleves_classe = [e for e in system.eleves if e.classe == selected_classe]
        
        if eleves_classe:
            st.markdown(f"### Élèves de {selected_classe} - {selected_matiere}")
            
            with st.form("saisie_notes"):
                notes_data = []
                for eleve in eleves_classe[:10]:  # Limité à 10 pour la démo
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"{eleve.prenom} {eleve.nom}")
                    with col2:
                        note = st.number_input(
                            f"Note {eleve.prenom}",
                            min_value=0.0,
                            max_value=20.0,
                            value=10.0,
                            step=0.25,
                            key=f"note_{eleve.id}"
                        )
                    with col3:
                        coeff = st.selectbox(
                            "Coeff",
                            [1, 2, 3],
                            key=f"coeff_{eleve.id}"
                        )
                    
                    notes_data.append({
                        'eleve': eleve,
                        'note': note,
                        'coeff': coeff
                    })
                
                submitted = st.form_submit_button("💾 Enregistrer les notes")
                if submitted:
                    st.success("Notes enregistrées avec succès !")
                    # Ici, normalement, on ajouterait les notes au système
        else:
            st.info("Aucun élève dans cette classe.")
    
    with tab2:
        st.markdown("### Gestion des classes")
        
        # Affichage des classes
        for classe in classes:
            with st.expander(f"🎓 {classe}"):
                eleves_classe = [e for e in system.eleves if e.classe == classe]
                df_eleves = pd.DataFrame([{
                    'Nom': f"{e.prenom} {e.nom}",
                    'Date naissance': e.date_naissance
                } for e in eleves_classe])
                
                st.dataframe(df_eleves, use_container_width=True)
                st.metric("Effectif", len(eleves_classe))
    
    with tab3:
        st.markdown("### Statistiques par classe")
        
        selected_stats_classe = st.selectbox("Classe pour statistiques :", classes)
        
        if selected_stats_classe:
            eleves_classe = [e for e in system.eleves if e.classe == selected_stats_classe]
            moyennes = []
            
            for eleve in eleves_classe:
                moyenne = system.get_moyenne_by_eleve(eleve.id)
                moyennes.append(moyenne)
            
            if moyennes:
                df_stats = pd.DataFrame({'Moyennes': moyennes})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Moyenne de la classe", f"{sum(moyennes)/len(moyennes):.2f}/20")
                    st.metric("Meilleure moyenne", f"{max(moyennes):.2f}/20")
                    st.metric("Moyenne la plus basse", f"{min(moyennes):.2f}/20")
                
                with col2:
                    fig = px.histogram(df_stats, x='Moyennes', nbins=10,
                                     title=f"Distribution des moyennes - {selected_stats_classe}")
                    st.plotly_chart(fig, use_container_width=True)

def admin_dashboard():
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h2>⚙️ Tableau de bord Administrateur</h2>
        <p>Gestion complète du système scolaire</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Utilisateurs", "🏫 Élèves", "📈 Statistiques", "⚙️ Configuration"])
    
    with tab1:
        st.markdown("### Gestion des utilisateurs")
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            parents_count = len([u for u in system.users.values() if u.role == 'parent'])
            st.metric("Parents", parents_count)
        with col2:
            teachers_count = len([u for u in system.users.values() if u.role == 'enseignant'])
            st.metric("Enseignants", teachers_count)
        with col3:
            st.metric("Élèves", len(system.eleves))
        
        # Liste des utilisateurs
        users_data = []
        for username, user in system.users.items():
            users_data.append({
                'Username': username,
                'Nom': f"{user.prenom} {user.nom}",
                'Rôle': user.role,
                'Email': user.email,
                'Téléphone': user.telephone
            })
        
        df_users = pd.DataFrame(users_data)
        st.dataframe(df_users, use_container_width=True)
        
        # Ajout d'utilisateur (démonstration)
        st.markdown("### Ajouter un utilisateur")
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Nom d'utilisateur")
                new_password = st.text_input("Mot de passe", type="password")
                new_role = st.selectbox("Rôle", ["parent", "enseignant", "admin"])
            with col2:
                new_nom = st.text_input("Nom")
                new_prenom = st.text_input("Prénom")
                new_email = st.text_input("Email")
            
            if st.form_submit_button("➕ Ajouter l'utilisateur"):
                st.success("Utilisateur ajouté avec succès ! (démonstration)")
    
    with tab2:
        st.markdown("### Gestion des élèves")
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            filter_classe = st.multiselect("Filtrer par classe", 
                                         sorted(list(set([e.classe for e in system.eleves]))))
        with col2:
            search_name = st.text_input("Rechercher par nom")
        
        # Affichage des élèves
        eleves_filtres = system.eleves
        if filter_classe:
            eleves_filtres = [e for e in eleves_filtres if e.classe in filter_classe]
        if search_name:
            eleves_filtres = [e for e in eleves_filtres if search_name.lower() in f"{e.nom} {e.prenom}".lower()]
        
        if eleves_filtres:
            eleves_data = []
            for eleve in eleves_filtres[:50]:  # Limité à 50 pour la démo
                moyenne = system.get_moyenne_by_eleve(eleve.id)
                eleves_data.append({
                    'ID': eleve.id,
                    'Nom': f"{eleve.prenom} {eleve.nom}",
                    'Classe': eleve.classe,
                    'Date naissance': eleve.date_naissance,
                    'Moyenne': moyenne
                })
            
            df_eleves = pd.DataFrame(eleves_data)
            st.dataframe(
                df_eleves,
                column_config={
                    "Moyenne": st.column_config.ProgressColumn(
                        "Moyenne",
                        help="Moyenne générale de l'élève",
                        format="%.2f",
                        min_value=0,
                        max_value=20,
                    ),
                },
                use_container_width=True
            )
        else:
            st.info("Aucun élève trouvé avec ces filtres.")
    
    with tab3:
        st.markdown("### Statistiques générales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_eleves = len(system.eleves)
            st.metric("Total élèves", total_eleves)
        
        with col2:
            total_notes = len(system.notes)
            st.metric("Total notes", total_notes)
        
        with col3:
            total_activites = len(system.activites)
            st.metric("Activités", total_activites)
        
        with col4:
            # Calcul de la moyenne générale de l'école
            moyennes = [system.get_moyenne_by_eleve(e.id) for e in system.eleves]
            moyenne_ecole = sum(moyennes) / len(moyennes) if moyennes else 0
            st.metric("Moyenne école", f"{moyenne_ecole:.2f}/20")
        
        # Graphique de répartition par classe
        st.markdown("### Répartition par classe")
        classes_count = {}
        for eleve in system.eleves:
            classes_count[eleve.classe] = classes_count.get(eleve.classe, 0) + 1
        
        df_classes = pd.DataFrame(list(classes_count.items()), columns=['Classe', 'Effectif'])
        df_classes = df_classes.sort_values('Effectif', ascending=False)
        
        fig = px.bar(df_classes, x='Classe', y='Effectif',
                    title="Effectif par classe",
                    color='Effectif',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### Configuration du système")
        
        st.info("Cette section permet de configurer les paramètres généraux de l'application.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Paramètres généraux")
            annee_scolaire = st.text_input("Année scolaire", "2023-2024")
            nom_ecole = st.text_input("Nom de l'école", "École Excellence Ivoirienne")
            ville = st.text_input("Ville", "Abidjan")
            
            st.markdown("#### Notifications")
            notif_email = st.checkbox("Activer notifications email", True)
            notif_sms = st.checkbox("Activer notifications SMS", True)
        
        with col2:
            st.markdown("#### Paramètres académiques")
            date_rentree = st.date_input("Date de rentrée", datetime(2024, 9, 2))
            date_vacances = st.date_input("Début des vacances", datetime(2024, 12, 21))
            
            st.markdown("#### Sécurité")
            session_timeout = st.slider("Timeout session (minutes)", 15, 120, 30)
            force_complex_password = st.checkbox("Forcer mots de passe complexes", True)
        
        if st.button("💾 Sauvegarder la configuration", use_container_width=True):
            st.success("Configuration sauvegardée avec succès !")

# ============================================
# APPLICATION PRINCIPALE
# ============================================

def main():
    display_header()
    
    if not st.session_state.logged_in:
        login_form()
    else:
        user = st.session_state.current_user
        
        # Navigation selon le rôle
        if user.role == 'parent':
            parent_dashboard()
        elif user.role == 'enseignant':
            teacher_dashboard()
        elif user.role == 'admin':
            admin_dashboard()
        else:
            st.error("Rôle utilisateur non reconnu")

if __name__ == "__main__":
    main()