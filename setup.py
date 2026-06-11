# Setup file for creating executable with PyInstaller
from setuptools import setup

setup(
    name="DnD-Virtual-DM",
    version="1.0",
    description="Donjons & Dragons - Maître du Jeu Virtuel",
    author="Mehwing",
    windows=[
        {
            'script': 'main.py',
            'icon': 'dnd_icon.ico',
        }
    ],
    options={
        'build_exe': {
            'include_files': ['dnd_icon.ico'],
        }
    }
)
