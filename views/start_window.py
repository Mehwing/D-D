"""
Start window for D&D application
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional, Callable
import os

from models.scenario import Scenario, ScenarioParser, create_sample_scenario
from models.character import Character, create_random_character


class StartWindow:
    """Window for selecting scenario and number of players"""
    
    def __init__(self, root: tk.Tk, on_start: Callable[[Scenario, List[Character]], None]):
        """
        Initialize the start window
        
        Args:
            root: Tkinter root window
            on_start: Callback function when game starts
        """
        self.root = root
        self.on_start = on_start
        self.scenario: Optional[Scenario] = None
        self.num_players = 1
        self.characters: List[Character] = []
        
        # Configure root window
        self.root.title("Donjons & Dragons - Démarrage")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Set window icon (placeholder)
        try:
            self.root.iconbitmap(default='dnd_icon.ico')
        except:
            pass
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface"""
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="Donjons & Dragons",
            font=('Arial', 24, 'bold')
        )
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(
            self.main_frame,
            text="Maître du Jeu Virtuel",
            font=('Arial', 14, 'italic')
        )
        subtitle_label.pack(pady=5)
        
        # Scenario selection frame
        scenario_frame = ttk.LabelFrame(self.main_frame, text="Sélection du Scénario", padding="10")
        scenario_frame.pack(fill=tk.X, pady=10)
        
        # Scenario options
        self.scenario_var = tk.StringVar(value="sample")
        
        scenario_options = [
            ("Scénario d'exemple", "sample"),
            ("Charger un fichier", "file"),
        ]
        
        for text, value in scenario_options:
            rb = ttk.Radiobutton(
                scenario_frame,
                text=text,
                variable=self.scenario_var,
                value=value,
                command=self._on_scenario_change
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # File selection button
        self.file_path_var = tk.StringVar()
        file_button = ttk.Button(
            scenario_frame,
            text="Parcourir...",
            command=self._browse_file
        )
        file_button.pack(pady=5)
        
        self.file_label = ttk.Label(scenario_frame, text="", foreground="gray")
        self.file_label.pack()
        
        # Scenario description
        self.scenario_desc_label = ttk.Label(
            scenario_frame,
            text="",
            wraplength=700,
            justify=tk.LEFT
        )
        self.scenario_desc_label.pack(fill=tk.X, pady=5)
        
        # Number of players frame
        players_frame = ttk.LabelFrame(self.main_frame, text="Nombre de Joueurs", padding="10")
        players_frame.pack(fill=tk.X, pady=10)
        
        # Player count slider
        self.num_players_var = tk.IntVar(value=1)
        
        players_slider = ttk.Scale(
            players_frame,
            from_=1,
            to=6,
            variable=self.num_players_var,
            command=lambda v: self.num_players_label.config(text=f"{int(float(v))} joueur(s)")
        )
        players_slider.pack(fill=tk.X, padx=20, pady=10)
        
        self.num_players_label = ttk.Label(players_frame, text="1 joueur(s)")
        self.num_players_label.pack()
        
        # Character creation options
        char_frame = ttk.LabelFrame(self.main_frame, text="Création des Personnages", padding="10")
        char_frame.pack(fill=tk.X, pady=10)
        
        self.char_creation_var = tk.StringVar(value="random")
        
        char_options = [
            ("Générer des personnages aléatoires", "random"),
            ("Créer des personnages manuellement", "manual"),
        ]
        
        for text, value in char_options:
            rb = ttk.Radiobutton(
                char_frame,
                text=text,
                variable=self.char_creation_var,
                value=value
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # Start button
        start_button = ttk.Button(
            self.main_frame,
            text="Commencer la Partie",
            command=self._start_game,
            style="Accent.TButton"
        )
        start_button.pack(pady=20)
        
        # Load sample scenario by default
        self._load_sample_scenario()
        
        # Configure styles
        self._configure_styles()
    
    def _configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        
        # Accent button style
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#8B0000",  # Dark red
            font=('Arial', 12, 'bold'),
            padding=10
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#A00000"), ("disabled", "#400000")]
        )
        
        # Frame styling
        style.configure(
            "TFrame",
            background="#f0f0f0"
        )
        style.configure(
            "TLabelFrame",
            background="#f0f0f0"
        )
        style.configure(
            "TLabel",
            background="#f0f0f0"
        )
    
    def _on_scenario_change(self):
        """Handle scenario selection change"""
        if self.scenario_var.get() == "sample":
            self._load_sample_scenario()
        else:
            self._load_file_scenario()
    
    def _load_sample_scenario(self):
        """Load the sample scenario"""
        self.scenario = create_sample_scenario()
        self.file_path_var.set("")
        self.file_label.config(text="Scénario: La Forêt Interdite")
        self.scenario_desc_label.config(
            text=self.scenario.description
        )
    
    def _load_file_scenario(self):
        """Load scenario from file"""
        file_path = self.file_path_var.get()
        if file_path and os.path.exists(file_path):
            try:
                self.scenario = ScenarioParser.parse_scenario_file(file_path)
                self.file_label.config(text=f"Fichier: {os.path.basename(file_path)}")
                self.scenario_desc_label.config(
                    text=self.scenario.description
                )
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de chargement du scénario: {e}")
                self.scenario = None
        else:
            self.scenario = None
            self.file_label.config(text="Aucun fichier sélectionné")
            self.scenario_desc_label.config(text="")
    
    def _browse_file(self):
        """Browse for scenario file"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier de scénario",
            filetypes=[
                ("Fichiers de scénario", "*.txt;*.scenario"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.scenario_var.set("file")
            self._load_file_scenario()
    
    def _start_game(self):
        """Start the game"""
        if not self.scenario:
            messagebox.showerror("Erreur", "Veuillez sélectionner un scénario valide")
            return
        
        self.num_players = self.num_players_var.get()
        
        # Create characters
        self.characters = []
        
        if self.char_creation_var.get() == "random":
            # Generate random characters
            for i in range(self.num_players):
                char = create_random_character()
                self.characters.append(char)
        else:
            # For now, still generate random characters
            # Manual creation would be implemented in CharacterCreationWindow
            for i in range(self.num_players):
                char = create_random_character()
                self.characters.append(char)
        
        # Start the game
        self.on_start(self.scenario, self.characters)
    
    def show(self):
        """Show the start window"""
        self.root.deiconify()
        self.root.lift()
    
    def hide(self):
        """Hide the start window"""
        self.root.withdraw()


# Import for type hints
from models.scenario import Scenario
from models.character import Character
