"""
Character sheet window for D&D application
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from models.character import Character, Race, Class, Alignment
from models.item import Weapon, Armor


class CharacterSheetWindow:
    """Window for displaying character sheet"""
    
    def __init__(self, root: tk.Tk, character: Character, on_close: Callable[[], None]):
        """
        Initialize the character sheet window
        
        Args:
            root: Tkinter root window
            character: The character to display
            on_close: Callback when window is closed
        """
        self.root = root
        self.character = character
        self.on_close = on_close
        
        # Create top-level window
        self.window = tk.Toplevel(root)
        self.window.title(f"Fiche de Personnage - {character.name}")
        self.window.geometry("800x700")
        self.window.minsize(700, 600)
        self.window.transient(root)
        self.window.grab_set()
        
        # Set window icon
        try:
            self.window.iconbitmap(default='dnd_icon.ico')
        except:
            pass
        
        # Create main frame
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI
        self._create_ui()
        
        # Configure styles
        self._configure_styles()
        
        # Protocol for window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _create_ui(self):
        """Create the user interface"""
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text=f"{self.character.name}",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=5)
        
        # Basic info frame
        basic_frame = ttk.LabelFrame(self.main_frame, text="Informations de Base", padding="10")
        basic_frame.pack(fill=tk.X, pady=5)
        
        # Character info in grid
        info_labels = [
            ("Race:", self.character.race.value),
            ("Classe:", self.character.char_class.value),
            ("Niveau:", str(self.character.level)),
            ("Alignement:", self.character.alignment.value),
            ("Expérience:", f"{self.character.experience} XP"),
        ]
        
        for i, (label, value) in enumerate(info_labels):
            ttk.Label(basic_frame, text=label, font=('Arial', 10)).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(basic_frame, text=value, font=('Arial', 10)).grid(row=i, column=1, sticky=tk.W, pady=2)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.main_frame, text="Caractéristiques", padding="10")
        stats_frame.pack(fill=tk.X, pady=5)
        
        # Stats in grid
        stats = [
            ("Force (FOR)", self.character.stats.strength, self.character.stats.strength_modifier),
            ("Dextérité (DEX)", self.character.stats.dexterity, self.character.stats.dexterity_modifier),
            ("Constitution (CON)", self.character.stats.constitution, self.character.stats.constitution_modifier),
            ("Intelligence (INT)", self.character.stats.intelligence, self.character.stats.intelligence_modifier),
            ("Sagesse (SAG)", self.character.stats.wisdom, self.character.stats.wisdom_modifier),
            ("Charisme (CHA)", self.character.stats.charisma, self.character.stats.charisma_modifier),
        ]
        
        for i, (stat_name, stat_value, modifier) in enumerate(stats):
            ttk.Label(stats_frame, text=stat_name, font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(stats_frame, text=str(stat_value), font=('Arial', 10)).grid(row=i, column=1, sticky=tk.W, pady=2)
            mod_label = ttk.Label(stats_frame, text=f"({modifier:+d})", font=('Arial', 10))
            mod_label.grid(row=i, column=2, sticky=tk.W, pady=2)
            
            # Color modifier based on value
            if modifier > 0:
                mod_label.config(foreground="#2E8B57")  # Green
            elif modifier < 0:
                mod_label.config(foreground="#8B0000")  # Red
        
        # Combat info frame
        combat_frame = ttk.LabelFrame(self.main_frame, text="Combat", padding="10")
        combat_frame.pack(fill=tk.X, pady=5)
        
        combat_labels = [
            ("Classe d'Armure (CA):", str(self.character.armor_class)),
            ("Points de Vie (PV):", f"{self.character.current_hp}/{self.character.max_hp}"),
            ("Initiative:", f"+{self.character.initiative}"),
            ("Vitesse:", f"{self.character.speed} pieds"),
            ("Bonus de maîtrise:", f"+{self.character.proficiency_bonus}"),
        ]
        
        for i, (label, value) in enumerate(combat_labels):
            ttk.Label(combat_frame, text=label, font=('Arial', 10)).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(combat_frame, text=value, font=('Arial', 10)).grid(row=i, column=1, sticky=tk.W, pady=2)
        
        # Health bar
        health_frame = ttk.Frame(combat_frame)
        health_frame.grid(row=1, column=2, sticky=tk.W, padx=10)
        
        health_canvas = tk.Canvas(health_frame, height=15, width=100, bg="#ccc", highlightthickness=0)
        health_canvas.pack()
        
        health_percent = self.character.current_hp / self.character.max_hp if self.character.max_hp > 0 else 0
        health_canvas.create_rectangle(
            0, 0, 100 * health_percent, 15,
            fill="#4CAF50" if health_percent > 0.5 else "#FFC107" if health_percent > 0.25 else "#F44336",
            outline=""
        )
        
        # Skills frame
        skills_frame = ttk.LabelFrame(self.main_frame, text="Compétences", padding="10")
        skills_frame.pack(fill=tk.X, pady=5)
        
        # Display skills
        if self.character.skills:
            for i, skill in enumerate(self.character.skills):
                ttk.Label(skills_frame, text=f"• {skill}", font=('Arial', 9)).pack(anchor=tk.W)
        else:
            ttk.Label(skills_frame, text="Aucune compétence", font=('Arial', 9, 'italic')).pack()
        
        # Features frame
        features_frame = ttk.LabelFrame(self.main_frame, text="Capacités", padding="10")
        features_frame.pack(fill=tk.X, pady=5)
        
        # Display features
        if self.character.features:
            for i, feature in enumerate(self.character.features):
                ttk.Label(features_frame, text=f"• {feature}", font=('Arial', 9)).pack(anchor=tk.W)
        else:
            ttk.Label(features_frame, text="Aucune capacité spéciale", font=('Arial', 9, 'italic')).pack()
        
        # Equipment frame
        equipment_frame = ttk.LabelFrame(self.main_frame, text="Équipement", padding="10")
        equipment_frame.pack(fill=tk.X, pady=5)
        
        # Weapons
        ttk.Label(equipment_frame, text="Armes:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        if self.character.weapons:
            for weapon in self.character.weapons:
                ttk.Label(equipment_frame, text=f"  - {weapon.name} ({weapon.damage_dice})", font=('Arial', 9)).pack(anchor=tk.W)
        else:
            ttk.Label(equipment_frame, text="  Aucune arme", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # Armor
        ttk.Label(equipment_frame, text="Armure:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 0))
        if self.character.armor:
            ttk.Label(equipment_frame, text=f"  - {self.character.armor.name} (CA {self.character.armor.armor_class})", font=('Arial', 9)).pack(anchor=tk.W)
        else:
            ttk.Label(equipment_frame, text="  Aucune armure", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # Shield
        ttk.Label(equipment_frame, text="Bouclier:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 0))
        shield_text = "Oui" if self.character.shield else "Non"
        ttk.Label(equipment_frame, text=f"  - {shield_text}", font=('Arial', 9)).pack(anchor=tk.W)
        
        # Spellcasting frame (if applicable)
        if self.character.known_spells or self.character.spell_slots:
            spell_frame = ttk.LabelFrame(self.main_frame, text="Lanceur de Sorts", padding="10")
            spell_frame.pack(fill=tk.X, pady=5)
            
            # Spell slots
            if self.character.spell_slots:
                ttk.Label(spell_frame, text="Emplacements de sorts:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                for level, count in sorted(self.character.spell_slots.items()):
                    ttk.Label(spell_frame, text=f"  Niveau {level}: {count}", font=('Arial', 9)).pack(anchor=tk.W)
            
            # Known spells
            if self.character.known_spells:
                ttk.Label(spell_frame, text="Sorts connus:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 0))
                for spell_name in self.character.known_spells:
                    ttk.Label(spell_frame, text=f"  • {spell_name}", font=('Arial', 9)).pack(anchor=tk.W)
        
        # Inventory frame
        inventory_frame = ttk.LabelFrame(self.main_frame, text="Inventaire", padding="10")
        inventory_frame.pack(fill=tk.X, pady=5)
        
        # Display inventory
        if self.character.inventory:
            for item in self.character.inventory[:10]:  # Show first 10 items
                ttk.Label(inventory_frame, text=f"• {item.name}", font=('Arial', 9)).pack(anchor=tk.W)
            if len(self.character.inventory) > 10:
                ttk.Label(inventory_frame, text=f"... et {len(self.character.inventory) - 10} autres", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        else:
            ttk.Label(inventory_frame, text="Inventaire vide", font=('Arial', 9, 'italic')).pack()
        
        # Gold
        ttk.Label(inventory_frame, text=f"Or: {self.character.gold} pièces", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 0))
        
        # Close button
        close_button = ttk.Button(
            self.main_frame,
            text="Fermer",
            command=self._on_window_close
        )
        close_button.pack(pady=10)
    
    def _configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        
        # Frame styling
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
    
    def update_character(self, character: Character):
        """Update the character being displayed"""
        self.character = character
        self.window.title(f"Fiche de Personnage - {character.name}")
        
        # Recreate UI with new character
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self._create_ui()
    
    def _on_window_close(self):
        """Handle window close"""
        self.window.destroy()
        self.on_close()
    
    def show(self):
        """Show the window"""
        self.window.deiconify()
        self.window.lift()
    
    def hide(self):
        """Hide the window"""
        self.window.withdraw()


# Import for type hints
from models.character import Character
