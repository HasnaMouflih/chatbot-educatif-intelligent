@echo off
TITLE Lancement de Jupyter Notebook
echo ===================================================
echo 🚀 INITIALISATION DE L'ENVIRONNEMENT DEEP LEARNING
echo ===================================================

:: 1. Se placer dans le dossier où se trouve ce fichier (Racine du projet)
cd /d "%~dp0"

:: 2. Vérifier et Activer l'environnement virtuel 'env'
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
    echo ✅ Environnement virtuel 'env' activé avec succès.
) else (
    echo ❌ ERREUR CRITIQUE : Le dossier 'env' est introuvable !
    echo Assurez-vous d'être à la racine du projet.
    pause
    exit
)

:: 3. Vérifier si Jupyter est installé, sinon l'installer
pip show notebook >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Jupyter Notebook n'est pas installé. Installation en cours...
    pip install notebook
)

:: 4. Lancer Jupyter Notebook à la racine
echo.
echo 🌍 Lancement du serveur... Une fenetre va s'ouvrir.
echo (Ne fermez pas cette fenetre noire tant que vous travaillez)
echo ===================================================
jupyter notebook

pause