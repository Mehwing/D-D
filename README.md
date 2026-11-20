# Décompte de Voix

Petite application locale pour assister au décompte des voix lors d'un vote à main levée en séance de groupe.

## Lancer sans terminal

### Windows — exécutable
1. Installer Python (https://www.python.org) puis : `pip install pyinstaller`
2. Double-cliquer sur `build_exe.bat`
3. L'exécutable est créé ici : `dist\Vote-Counter.exe` — il se lance par double-clic, console masquée

### Windows — directement
Double-cliquer sur `vote_counter.py` (lance `pythonw`, sans fenêtre de console).

### Linux / macOS
Double-cliquer `vote_counter.py` après avoir associé l'extension `.py` à Python, ou lancer `python3 vote_counter.py`.

## Fonctionnement
- **Adhérents par parti** : 8 champs ; les champs vides sont simplement ignorés. Le total des adhérents inscrits est affiché.
- **Vote à main levée** : boutons **Pour** / **Contre** / **Abstention** pour compter les voix en direct, plus `-1` (annuler la dernière voix) et réinitialisation.
- **Abstentions** : exclues des voix exprimées, elles font baisser la majorité nécessaire.
- **Type de loi** :
  - *Loi basique* : majorité stricte de +1/2 des voix exprimées (l'égalité rejette).
  - *Loi constitutionnelle* : majorité des 2/3 des voix exprimées.
- **Résultat** : total des voix (avec et sans abstentions), seuil requis et verdict **LOI ACCEPTÉE** / **LOI REJETÉE**.

## Exigences
Python 3.8+ avec Tkinter (inclus dans l'installateur Windows officiel). Aucune autre dépendance.
