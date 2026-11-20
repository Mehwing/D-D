@echo off
:: Script pour créer l'exécutable Décompte de Voix avec PyInstaller
:: Nécessite PyInstaller : pip install pyinstaller
:: Résultat : dist\Vote-Counter.exe (double-cliquable, sans console)

python -m PyInstaller --onefile --windowed --name "Vote-Counter" vote_counter.py

echo.
echo Terminé : l'exécutable se trouve dans le dossier dist\Vote-Counter.exe
pause
