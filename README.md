# 🌱 e_agri – Plateforme web de vente de produits agricoles

## 🎯 Objectif du projet

Développer une application web permettant la mise en relation entre **vendeurs de produits agricoles** et **clients**, avec une gestion complète des utilisateurs, produits, commandes et paiements.

### Fonctionnalités principales

* Gestion des utilisateurs (clients et vendeurs)
* Gestion des produits agricoles
* Gestion des commandes et du panier
* Paiement en ligne
* Interface administrateur (via Django Admin)

---

## 🛠️ Technologies utilisées

* **Backend** : Django (Python)
* **Base de données** : PostgreSQL
* **ORM** : Django ORM
* **Gestion de versions** : Git & GitHub

---

## 📁 Structure du projet

```
e_agri/
├── agri_market/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── e_agri/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation du projet (OBLIGATOIRE pour chaque membre)

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/organisation/e_agri.git
cd e_agri
```

### 2️⃣ Créer et activer l'environnement virtuel

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Créer la base de données PostgreSQL (locale)

```sql
CREATE DATABASE e_agri;
```

### 5️⃣ Configurer la connexion DB

Modifier `settings.py` ou `.env` avec vos paramètres locaux.

### 6️⃣ Appliquer les migrations

```bash
python manage.py migrate
```

### 7️⃣ Créer un super utilisateur (admin Django)

```bash
python manage.py createsuperuser
```

### 8️⃣ Lancer le serveur

```bash
python manage.py runserver
```

---

## 🧱 Règles de travail en équipe (TRÈS IMPORTANT)

* ❌ Ne jamais modifier la base de données à la main
* ✅ Toute modification du schéma passe par `models.py`
* ✅ Toujours créer et pousser les migrations
* ❌ Ne jamais supprimer une migration déjà partagée
* ✅ Une branche Git par fonctionnalité

---

## 👥 Répartition des tâches (4 personnes)

### 👤 Rosvel – **Responsable Base de données & Models**

**Rôle clé (chef DB)**

* Création et mise à jour de `models.py`
* Gestion des relations entre les entités
* Création des migrations
* Validation du schéma global

📂 Fichiers :

* `models.py`
* `migrations/`

---

### 👤Franck – **Logique métier (Services)**

* Gestion du panier (`ajout`, `suppression`, `validation`)
* Calcul des montants
* Gestion des stocks
* Logique des paiements

📂 Fichiers :

* `services_panier.py`
* `services_paiement.py`

---

### 👤 Dufort – **Vues & API**

* Création des vues Django
* Connexion vues ↔ services
* Gestion des URLs
* Sécurité (authentification, permissions)

📂 Fichiers :

* `views.py`
* `urls.py`

---

### 👤 pavel  – **Interface & Tests**

* Templates HTML (si frontend Django)
* Tests unitaires
* Scénarios utilisateurs
* Documentation utilisateur

📂 Fichiers :

* `templates/`
* `tests.py`

---

## 🔄 Workflow Git recommandé

```bash
git checkout -b feature/nom_fonctionnalite
# coder
git add .
git commit -m "Ajout fonctionnalité X"
git push origin feature/nom_fonctionnalite
```

➡️ Pull Request obligatoire avant merge sur `main`

---

## ✅ Bonnes pratiques

* Tester avant chaque commit
* Commenter le code important
* Communiquer avant de modifier les models

