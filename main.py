"""
Main application file for D&D Virtual Dungeon Master
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from typing import List

from models.scenario import Scenario, create_sample_scenario
from models.character import Character, create_random_character

from views.start_window import StartWindow
from views.game_window import GameWindow


class DnDApplication:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        # Create main window
        self.root = tk.Tk()
        self.root.title("Donjons & Dragons - Maître du Jeu Virtuel")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Set window icon
        try:
            # Try to load icon from file
            icon_path = os.path.join(os.path.dirname(__file__), 'dnd_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
        except:
            pass
        
        # Configure styles
        self._configure_styles()
        
        # Create start window
        self.start_window = StartWindow(
            self.root,
            on_start=self._start_game
        )
        
        # Current game window
        self.game_window = None
        
        # Protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _configure_styles(self):
        """Configure global styles"""
        style = ttk.Style()
        
        # Set theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Configure default styles
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=('Arial', 10))
        style.configure("TButton", font=('Arial', 10))
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0", font=('Arial', 10, 'bold'))
    
    def _start_game(self, scenario: Scenario, characters: List[Character]):
        """Start a new game with the selected scenario and characters"""
        # Hide start window
        self.start_window.hide()
        
        # Create game window
        self.game_window = GameWindow(
            self.root,
            scenario,
            characters,
            on_quit=self._return_to_menu
        )
    
    def _return_to_menu(self):
        """Return to main menu"""
        if self.game_window:
            # Destroy game window
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Recreate start window
            self.start_window = StartWindow(
                self.root,
                on_start=self._start_game
            )
            
            self.game_window = None
    
    def _on_close(self):
        """Handle application close"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application?"):
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Set up environment
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
    
    # Create and run application
    app = DnDApplication()
    app.run()


# Import for type hints
from typing import List
from models.scenario import Scenario
from models.character import Character
