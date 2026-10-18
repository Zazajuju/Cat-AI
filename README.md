# 🐾 Cat AI - Desktop Pixel Cats with Local AI (Ollama)

> Des compagnons félins en pixel art, autonomes et interactifs, qui vivent sur votre bureau, discutent grâce à un modèle d'IA local (Ollama Gemma 3), accomplissent des quêtes, utilisent leurs accessoires et apportent de la vie à votre quotidien !

---

## 🗂️ Structure du Projet

Le projet est organisé en deux dossiers indépendants adaptés à chaque système d'exploitation :

```
Cat AI/
├── 🪟 windows/               # Version optimisée pour Windows (Barre des tâches)
│   ├── main.py              # Point d'entrée principal Windows
│   ├── cat_widget.py        # Physique, états et animations des chats
│   ├── accessory_widget.py  # Meubles & accessoires interactifs
│   ├── chat_dialog.py       # Fenêtre de dialogue 5 onglets (Chat, Règles, To-Do, Quêtes, Trésors)
│   ├── settings_dialog.py   # Menu complet de configuration
│   ├── sprites.py           # Banques de sprites pixel art et palettes
│   ├── ollama_worker.py     # Connecteur IA local (Ollama Gemma 3)
│   ├── memory_manager.py    # Système de mémoire et d'apprentissage
│   ├── quest_manager.py     # Quêtes quotidiennes & progression XP
│   ├── gift_manager.py      # Trésors virtuels trouvés sur le PC
│   ├── task_manager.py      # To-Do Lists individuelles par chat
│   ├── lancer_chats.bat     # Script de lancement rapide en 1 clic
│   └── requirements.txt     # Dépendances Python
│
├── 🍎 mac/                   # Version optimisée pour macOS (Dock & MenuBar)
│   ├── main.py              # Point d'entrée principal macOS
│   ├── cat_widget.py        # Physique adaptée au Dock macOS (sans ombres portées)
│   ├── accessory_widget.py  # Accessoires adaptés macOS
│   ├── ... (modules)        # Modules partagés identiques
│   ├── lancer_chats.sh      # Script de lancement exécutable macOS
│   └── requirements.txt     # Dépendances Python
│
├── requirements.txt         # Dépendances globales
└── README.md                # Documentation complète du projet
```

---

## 🌟 Fonctionnalités Principales

### 🐈 1. Comportement Félin & Physique Réaliste
- **Animations Pixel Art Détaillées** : Marche, course, observation assise, toilette, étirement, ronronnement avec cœurs, posture du pain (*loaf*), sommeil avec Zzz flottants, affût furtif (*stalk*), et bond acrobatique (*jump*).
- **Physique de Saut Aérien Parabolique** : Véritable impulsion verticale ascendante avec gravité réaliste et animation dynamique sur 4 frames (élan, extension en plein vol, descente, réception).
- **Agilité et Vitesses Uniques** : Chaque chat a une vitesse et une agilité propres selon sa personnalité (gourmand, joueur, philosophe, etc.).
- **Anti-Stacking Intelligent** : Répulsion douce pour empêcher les chats de se chevaucher, tout en leur permettant de se croiser librement lorsqu'ils marchent en directions opposées.
- **Pointeur Laser Interactif 🔴** : Activez le laser rouge pour que les chats le traquent et bondissent dans les airs pour l'attraper !

### 🛋️ 2. Mobilier & Accessoires Interactifs
Chaque meuble est déplaçable à la souris (Glisser-Déposer) et s'aimante automatiquement au sol :
- 🧺 **Panier Douillet** : Rendu dynamique multicouche (*layering*). Le chat s'installe au milieu sur le coussin velours rouge avec ses Zzz animés, enveloppé par le rebord en osier tressé.
- 🏠 **Petite Cabane** : Maisonnette en bois et toit de tuiles où les chats aiment s'abriter pour dormir au calme (yeux dorés visibles dans l'entrée).
- 🌳 **Arbre à Chat** : Poteau griffoir en corde sisal, souris suspendue et perchoir pour les grands sauts.
- 🥣 **Distributeur de Croquettes** : Bocal transparent avec logo poisson et gamelle pleine pour les repas.
- 💧 **Fontaine à Eau Fraîche** : Fontaine moderne avec marguerite et cascade d'eau bleue pour s'hydrater.
- **Menu Contextuel (Clic Droit sur chaque meuble)** : Appeler un chat ciblé, remplir les gamelles, ajouter de nouveaux meubles ou les ranger.

### 🧠 3. Intelligence Artificielle & Mémoire Locale (Ollama Gemma 3)
- **Discussion en Langage Naturel** : Cliquez sur un chat pour lui parler. Les réponses sont générées localement via Ollama (modèle `gemma3:1b` par défaut).
- **Personnalité Unique** : Chaque chat s'exprime selon son tempérament (Mochi le curieux, Luna la mystique, Félix l'aventurier, etc.).
- **Apprentissage de Règles Instantanées** : Apprenez des répliques personnalisées à chaque chat (*« Quand je dis X, réponds Y »*).
- **Discussions Autonomes & Pensées Spontanées** : Les chats discutent entre eux ou partagent leurs pensées à voix haute sur votre écran.
- **Mémoire Persistante** : Les chats se souviennent des faits partagés et de leur historique.

### 📋 4. To-Do List Personnelle par Chat
- Chaque chat dispose de sa propre liste de tâches à accomplir.
- Les chats vérifient régulièrement l'avancement de votre travail et célèbrent vos succès en sautant de joie !

### 🎯 5. Quêtes Félines & Niveaux d'Expérience (XP)
- Quêtes quotidiennes interactives (câlins, festin de croquettes, saut vers le laser, discussions, etc.).
- Barre de progression d'expérience et passage de niveaux.

### 🎁 6. Trésors Virtuels du PC
- Les chats partent fouiller les recoins de votre ordinateur et vous rapportent des trésors insolites (Câble RJ45 doré, Pixel d'or légendaire, Souris mécanique sacrée, etc.) classés par raretés (Commun, Rare, Épique, Légendaire).

---

## 🚀 Installation & Démarrage

### 1. Prérequis
- **Python 3.10 ou supérieur** : [python.org](https://www.python.org/downloads/)
- **Ollama** (pour l'IA locale) : [ollama.com](https://ollama.com/download)
  - Téléchargez le modèle léger recommandé :
    ```bash
    ollama run gemma3:1b
    ```

### 2. Installation des Dépendances
Dans un terminal, installez PyQt6 :
```bash
pip install -r requirements.txt
```

---

### 🪟 Lancement sur Windows

1. Rendez-vous dans le dossier `windows/` :
   ```powershell
   cd windows
   ```
2. Lancez simplement le script batch :
   - **Double-cliquez sur `lancer_chats.bat`**
   - Ou dans PowerShell / CMD :
     ```powershell
     python main.py
     ```

---

### 🍎 Lancement sur macOS

1. Rendez-vous dans le dossier `mac/` :
   ```bash
   cd mac
   ```
2. Donnez les permissions d'exécution au script si nécessaire :
   ```bash
   chmod +x lancer_chats.sh
   ```
3. Lancez le jeu :
   ```bash
   ./lancer_chats.sh
   # ou directement :
   python3 main.py
   ```

> **Note macOS** : L'icône de l'application apparaît dans la barre des menus supérieure. Les chats se déplacent naturellement au-dessus du Dock macOS sans aucune ombre rectangulaire gênante.

---

## 🎮 Commandes & Raccourcis

| Action | Contrôle |
|---|---|
| **Ouvrir le menu contextuel d'un chat** | Clic Droit sur le chat |
| **Parler / Discuter avec un chat** | Clic Gauche sur le chat |
| **Déplacer un chat ou un meuble** | Clic Gauche maintenu (Glisser-Déposer) |
| **Activer / Couper le Pointeur Laser** | Menu de la barre des tâches ou menu chat |
| **Ouvrir la To-Do List d'un chat** | Clic Droit sur le chat > 📋 To-Do List |
| **Consulter les Quêtes & Niveaux** | Clic Droit sur le chat > 🎯 Quêtes |
| **Inventaire des Trésors du PC** | Clic Droit sur le chat > 🎁 Trésors |
| **Fouiller le PC à la recherche d'un trésor** | Clic Droit sur le chat > 🔍 Fouiller le PC |
| **Menu des Paramètres** | Clic Droit sur l'icône de la barre des tâches > ⚙️ Menu de Configuration |

---

## ⚙️ Configuration & Personnalisation

Toutes les options sont modifiables directement depuis le **Menu de Configuration (GUI)** ou dans les fichiers JSON :
- `settings.json` : Vitesse, échelle des pixels, intervalles de bavardage, modèle Ollama.
- `memories.json` : Faits, souvenirs et règles apprises par chaque chat.
- `accessories.json` : Emplacements sauvegardés des meubles et paniers.
- `quests.json` : Progression des missions quotidiennes et points d'XP.
- `gifts.json` : Collection des trésors découverts.

---

## 📄 Licence

Projet libre et open-source sous licence **MIT**. Développé avec passion pour tous les amoureux des chats et du pixel art ! 🐾
