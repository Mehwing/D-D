@echo off
:: Script pour créer l'exécutable D&D avec PyInstaller
:: Nécessite PyInstaller : pip install pyinstaller

python -m PyInstaller --onefile --windowed --icon=dnd_icon.ico --name "DnD-Virtual-DM" main.py

pause
