# Donjons & Dragons - Maître du Jeu Virtuel

Une application complète pour jouer à Donjons & Dragons sans avoir besoin d'un maître du jeu humain. L'application gère les scénarios, les combats, les jets de dés, les personnages et bien plus encore!

## Fonctionnalités

### 🎲 Système de Dés
- Lancez tous les types de dés D&D (d4, d6, d8, d10, d12, d20, d100)
- Gestion des jets avec avantage/désavantage
- Modificateurs personnalisables
- Historique des jets

### 🧙 Système de Personnages
- Création de personnages aléatoires ou personnalisés
- 10 races disponibles (Humain, Elfe, Nain, Halfelin, Orc, Tieffelin, Dracónide, Gnome, Demi-Elfe, Demi-Orc)
- 12 classes disponibles (Guerrier, Magicien, Voleur, Clerc, Barbare, Paladin, Rôdeur, Moine, Barde, Druide, Ensorceleur, Occultiste)
- Gestion complète des statistiques (FOR, DEX, CON, INT, SAG, CHA)
- Calcul automatique des modificateurs
- Système de points de vie et classe d'armure
- Gestion des compétences et capacités spéciales
- Inventaire complet avec objets, armes, armures et potions
- Système de sorts pour les classes magiques

### ⚔️ Système de Combat
- Combats au tour par tour avec initiative
- Gestion des attaques, dégâts et jets de sauvegarde
- Système de combat automatique pour les ennemis
- Gestion des points de vie et de l'état des combattants
- Utilisation d'objets et de sorts pendant le combat
- Possibilité de fuir le combat

### 📜 Système de Scénarios
- Scénario d'exemple complet inclus (La Forêt Interdite)
- Chargement de scénarios depuis des fichiers texte
- Plusieurs types d'événements:
  - Texte narratif
  - Choix multiples
  - Combats
  - Jets de compétence
  - Pièges
  - Récompenses (objets, or, expérience)
  - Repos
- Conditions pour les événements (niveau, classe, objets en inventaire, etc.)
- Variables de scénario
- Système de progression linéaire ou branchée

### 🎯 Interface Utilisateur
- Interface graphique intuitive avec Tkinter
- Affichage des profils des personnages en temps réel
- Journal de combat détaillé
- Fenêtres dédiées pour:
  - Fiches de personnage complètes
  - Inventaire
  - Lanceur de dés
  - Combats

## Installation

### Prérequis
- Python 3.7 ou supérieur
- Tkinter (généralement inclus avec Python)

### Installation

1. Cloner le dépôt ou télécharger les fichiers
2. Naviguer dans le dossier du projet
3. Exécuter l'application:

```bash
python main.py
```

## Utilisation

### Démarrage
1. Lancez l'application avec `python main.py`
2. Sélectionnez un scénario (le scénario d'exemple est chargé par défaut)
3. Choisissez le nombre de joueurs (1 à 6)
4. Sélectionnez le mode de création des personnages (aléatoire ou manuel)
5. Cliquez sur "Commencer la Partie"

### Pendant la Partie
- **Fenêtre principale**: Affiche le texte du scénario et les choix disponibles
- **Panneau des personnages**: Affiche les profils de tous les personnages
- **Boutons d'action**:
  - "Fiche Complète": Affiche la fiche détaillée d'un personnage
  - "Inventaire": Gère l'inventaire du personnage
  - "Lancer de Dés": Ouvre le lanceur de dés
  - "Combattre": Commence un combat (quand disponible)
  - "Continuer": Passe à l'événement suivant
  - "Sauvegarder": Sauvegarde la partie (fonctionnalité à venir)
  - "Quitter": Retourne au menu principal

### Pendant un Combat
- Sélectionnez une cible et une arme pour attaquer
- Lancez des sorts si votre personnage en connaît
- Utilisez des objets de votre inventaire
- Terminez votre tour avec "Fin du tour"
- Les ennemis attaquent automatiquement

## Structure du Projet

```
D-D/
├── main.py                 # Point d'entrée de l'application
├── README.md               # Documentation
├── models/                 # Classes métiers
│   ├── __init__.py
│   ├── dice.py            # Système de dés
│   ├── character.py       # Personnages
│   ├── item.py            # Objets, armes, armures, potions
│   ├── spell.py           # Sorts
│   ├── combat.py          # Combats et ennemis
│   └── scenario.py        # Scénarios et événements
├── views/                  # Interfaces graphiques
│   ├── __init__.py
│   ├── start_window.py    # Fenêtre de démarrage
│   ├── game_window.py     # Fenêtre principale de jeu
│   ├── combat_window.py   # Fenêtre de combat
│   ├── dice_roller_window.py  # Lanceur de dés
│   ├── inventory_window.py    # Inventaire
│   └── character_sheet_window.py # Fiche de personnage
└── scenarios/              # Fichiers de scénarios
    └── foret_interdite.txt # Scénario d'exemple
```

## Format des Fichiers de Scénario

Les scénarios sont des fichiers texte avec un format simple:

```
[scenario]
title: Nom du scénario
description: Description du scénario
author: Auteur

[event:start]
type: text
title: Titre de l'événement
text: Texte à afficher
next: event_id_suivant

[event:event_id]
type: choice
text: Texte avec choix
choice1: Texte du choix -> event_cible
choice2: Autre choix -> autre_event

[event:combat_event]
type: combat
combat: nom_du_combat_prédéfinis
next: event_apres_combat

[event:check_event]
type: check
skill: nom_de_la_compétence
dc: difficulté
success: event_si_reussite
failure: event_si_echec
```

Types d'événements disponibles:
- `text`: Texte simple
- `dialogue`: Dialogue
- `choice`: Choix multiples
- `combat`: Combat
- `check`: Jet de compétence
- `reward`: Récompense
- `trap`: Piège
- `puzzle`: Énigme
- `rest`: Repos
- `end`: Fin du scénario

## Personnalisation

### Ajouter de Nouveaux Objets
Éditez `models/item.py` et ajoutez de nouveaux objets dans les dictionnaires:
- `WEAPONS` pour les armes
- `ARMORS` pour les armures
- `POTIONS` pour les potions
- `MISC_ITEMS` pour les objets divers

### Ajouter de Nouveaux Ennemis
Éditez `models/combat.py` et ajoutez de nouveaux ennemis dans le dictionnaire `ENEMIES`.

### Ajouter de Nouveaux Sorts
Éditez `models/spell.py` et ajoutez de nouveaux sorts dans les dictionnaires:
- `CANTRIPS` pour les tours de magie
- `LEVEL_1_SPELLS` pour les sorts de niveau 1
- `LEVEL_2_SPELLS` pour les sorts de niveau 2

### Créer de Nouveaux Scénarios
Créez un nouveau fichier dans le dossier `scenarios/` en suivant le format décrit ci-dessus.

## Contribution

Les contributions sont les bienvenues! Vous pouvez:
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Ajouter de nouveaux scénarios
- Améliorer le code existant

## Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, le modifier et le distribuer comme vous le souhaitez.

## Remerciements

- À tous les fans de Donjons & Dragons
- À la communauté Python
- Aux créateurs de Tkinter pour cette bibliothèque d'interface graphique

---

**Bon jeu et que les dés vous soient favorables! 🎲✨**
