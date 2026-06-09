"""
Combat window for D&D application
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable, Tuple

from models.character import Character
from models.combat import Combat, Enemy
from models.dice import Dice, DiceResult
from models.item import Weapon


class CombatWindow:
    """Window for handling combat encounters"""
    
    def __init__(self, root: tk.Tk, combat: Combat, characters: List[Character], on_combat_end: Callable[[str], None]):
        """
        Initialize the combat window
        
        Args:
            root: Tkinter root window
            combat: The combat encounter
            characters: List of player characters
            on_combat_end: Callback when combat ends
        """
        self.root = root
        self.combat = combat
        self.characters = characters
        self.on_combat_end = on_combat_end
        
        # Create top-level window
        self.window = tk.Toplevel(root)
        self.window.title(f"Combat - {combat.name}")
        self.window.geometry("900x600")
        self.window.minsize(700, 500)
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
        
        # Start combat
        self._start_combat()
    
    def _create_ui(self):
        """Create the user interface"""
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text=f"Combat: {self.combat.name}",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=5)
        
        # Round and turn info
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.round_label = ttk.Label(
            self.info_frame,
            text=f"Round: {self.combat.current_round}",
            font=('Arial', 10)
        )
        self.round_label.pack(side=tk.LEFT, padx=10)
        
        self.turn_label = ttk.Label(
            self.info_frame,
            text="Tour: —",
            font=('Arial', 10)
        )
        self.turn_label.pack(side=tk.LEFT, padx=10)
        
        # Main combat area
        combat_area = ttk.Panedwindow(self.main_frame, orient=tk.HORIZONTAL)
        combat_area.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - combatants list
        self.left_panel = ttk.Frame(combat_area, width=250, padding="10")
        combat_area.add(self.left_panel, width=250)
        
        # Right panel - combat log and actions
        self.right_panel = ttk.Frame(combat_area, padding="10")
        combat_area.add(self.right_panel)
        
        # Create left panel
        self._create_left_panel()
        
        # Create right panel
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create the left panel with combatants list"""
        # Title
        title_label = ttk.Label(
            self.left_panel,
            text="Ordre des Tours",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(fill=tk.X, pady=5)
        
        # Turn order list
        self.turn_order_frame = ttk.Frame(self.left_panel)
        self.turn_order_frame.pack(fill=tk.BOTH, expand=True)
        
        # Combatants list
        self.combatants_frame = ttk.Frame(self.left_panel)
        self.combatants_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Title for combatants
        combatants_title = ttk.Label(
            self.combatants_frame,
            text="Combattants",
            font=('Arial', 10, 'bold')
        )
        combatants_title.pack(fill=tk.X, pady=(0, 5))
        
        # Players frame
        self.players_frame = ttk.LabelFrame(self.combatants_frame, text="Joueurs", padding="5")
        self.players_frame.pack(fill=tk.X, pady=2)
        
        # Enemies frame
        self.enemies_frame = ttk.LabelFrame(self.combatants_frame, text="Ennemis", padding="5")
        self.enemies_frame.pack(fill=tk.X, pady=2)
    
    def _create_right_panel(self):
        """Create the right panel with combat log and actions"""
        # Combat log frame
        log_frame = ttk.LabelFrame(self.right_panel, text="Journal de Combat", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Combat log text area
        self.combat_log = tk.Text(
            log_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            state=tk.DISABLED,
            bg="#f8f8f8"
        )
        self.combat_log.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, command=self.combat_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.combat_log.config(yscrollcommand=scrollbar.set)
        
        # Action frame
        action_frame = ttk.LabelFrame(self.right_panel, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=10)
        
        # Current combatant info
        self.current_combatant_frame = ttk.Frame(action_frame)
        self.current_combatant_frame.pack(fill=tk.X, pady=5)
        
        self.current_combatant_label = ttk.Label(
            self.current_combatant_frame,
            text="Tour de: —",
            font=('Arial', 10, 'bold')
        )
        self.current_combatant_label.pack(side=tk.LEFT)
        
        # Action buttons
        self.action_buttons_frame = ttk.Frame(action_frame)
        self.action_buttons_frame.pack(fill=tk.X, pady=5)
        
        # Attack button
        self.attack_button = ttk.Button(
            self.action_buttons_frame,
            text="Attaquer",
            command=self._show_attack_dialog,
            style="Combat.TButton"
        )
        self.attack_button.pack(side=tk.LEFT, padx=5)
        
        # Cast spell button
        self.spell_button = ttk.Button(
            self.action_buttons_frame,
            text="Lancer un sort",
            command=self._show_spell_dialog,
            style="Spell.TButton"
        )
        self.spell_button.pack(side=tk.LEFT, padx=5)
        
        # Use item button
        self.item_button = ttk.Button(
            self.action_buttons_frame,
            text="Utiliser un objet",
            command=self._show_item_dialog,
            style="Item.TButton"
        )
        self.item_button.pack(side=tk.LEFT, padx=5)
        
        # End turn button
        self.end_turn_button = ttk.Button(
            self.action_buttons_frame,
            text="Fin du tour",
            command=self._end_turn,
            style="Accent.TButton"
        )
        self.end_turn_button.pack(side=tk.RIGHT, padx=5)
        
        # Flee button
        flee_button = ttk.Button(
            self.action_buttons_frame,
            text="Fuir",
            command=self._flee_combat,
            style="Flee.TButton"
        )
        flee_button.pack(side=tk.RIGHT, padx=5)
    
    def _configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        
        # Combat button style
        style.configure(
            "Combat.TButton",
            foreground="white",
            background="#8B0000",  # Dark red
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Combat.TButton",
            background=[("active", "#A00000"), ("disabled", "#400000")]
        )
        
        # Spell button style
        style.configure(
            "Spell.TButton",
            foreground="white",
            background="#4682B4",  # Steel blue
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Spell.TButton",
            background=[("active", "#5A9BD5"), ("disabled", "#284768")]
        )
        
        # Item button style
        style.configure(
            "Item.TButton",
            foreground="white",
            background="#2E8B57",  # Sea green
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Item.TButton",
            background=[("active", "#3CB371"), ("disabled", "#1E5B39")]
        )
        
        # Accent button style
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#8B4513",  # Saddle brown
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#A0522D"), ("disabled", "#402813")]
        )
        
        # Flee button style
        style.configure(
            "Flee.TButton",
            foreground="white",
            background="#808080",  # Gray
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Flee.TButton",
            background=[("active", "#A0A0A0"), ("disabled", "#404040")]
        )
        
        # Frame styling
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
    
    def _start_combat(self):
        """Start the combat"""
        # Display initial message
        self._add_to_log(f"Combat commencé: {self.combat.description}")
        
        # Display turn order
        self._display_turn_order()
        
        # Display combatants
        self._display_combatants()
        
        # Set current turn
        self._update_turn_info()
    
    def _display_turn_order(self):
        """Display the turn order"""
        # Clear existing turn order
        for widget in self.turn_order_frame.winfo_children():
            widget.destroy()
        
        # Display turn order
        for i, (name, initiative, is_player) in enumerate(self.combat.turn_order):
            side = "Joueur" if is_player else "Ennemi"
            
            # Highlight current turn
            if i == self.combat.current_turn:
                bg_color = "#FFE4B5"  # Light yellow
            else:
                bg_color = "#f0f0f0"
            
            turn_frame = ttk.Frame(self.turn_order_frame, padding="2", style="Turn.TFrame")
            turn_frame.pack(fill=tk.X, pady=1)
            
            # Configure frame background
            turn_frame.configure(style="Turn.TFrame")
            
            ttk.Label(
                turn_frame,
                text=f"{i+1}. {name} ({side}, Init: {initiative})",
                font=('Arial', 9)
            ).pack(fill=tk.X)
    
    def _display_combatants(self):
        """Display combatants in their respective frames"""
        # Clear existing combatants
        for widget in self.players_frame.winfo_children():
            widget.destroy()
        for widget in self.enemies_frame.winfo_children():
            widget.destroy()
        
        # Display players
        for character, initiative in self.combat.combatants:
            self._display_combatant(self.players_frame, character.name, character.current_hp, character.max_hp, True)
        
        # Display enemies
        for enemy, initiative in self.combat.enemies_in_combat:
            self._display_combatant(self.enemies_frame, enemy.name, enemy.current_hp, enemy.hit_points, False)
    
    def _display_combatant(self, parent_frame: ttk.Frame, name: str, current_hp: int, max_hp: int, is_player: bool):
        """Display a single combatant"""
        combatant_frame = ttk.Frame(parent_frame, padding="2")
        combatant_frame.pack(fill=tk.X, pady=1)
        
        # Name and HP
        hp_percent = current_hp / max_hp if max_hp > 0 else 0
        hp_color = "#4CAF50" if hp_percent > 0.5 else "#FFC107" if hp_percent > 0.25 else "#F44336"
        
        # Status indicator
        status = "OK" if current_hp > 0 else "INCONSCIENT" if is_player else "VAINCU"
        
        info_label = ttk.Label(
            combatant_frame,
            text=f"{name}: {current_hp}/{max_hp} PV [{status}]",
            font=('Arial', 9)
        )
        info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # HP bar
        hp_canvas = tk.Canvas(combatant_frame, height=10, width=80, bg="#ccc", highlightthickness=0)
        hp_canvas.pack(side=tk.RIGHT, padx=5)
        hp_canvas.create_rectangle(
            0, 0, 80 * hp_percent, 10,
            fill=hp_color,
            outline=""
        )
    
    def _update_turn_info(self):
        """Update turn information"""
        current_combatant = self.combat.get_current_combatant()
        
        if current_combatant:
            name, is_player = current_combatant
            self.turn_label.config(text=f"Tour: {self.combat.current_turn + 1}")
            self.current_combatant_label.config(text=f"Tour de: {name}")
            
            # Enable/disable action buttons based on who's turn it is
            if is_player:
                # Player's turn - enable actions
                self.attack_button.config(state=tk.NORMAL)
                self.spell_button.config(state=tk.NORMAL)
                self.item_button.config(state=tk.NORMAL)
                self.end_turn_button.config(state=tk.NORMAL)
            else:
                # Enemy's turn - disable player actions
                self.attack_button.config(state=tk.DISABLED)
                self.spell_button.config(state=tk.DISABLED)
                self.item_button.config(state=tk.DISABLED)
                self.end_turn_button.config(state=tk.DISABLED)
                
                # Auto-process enemy turn
                self._process_enemy_turn()
        else:
            self.current_combatant_label.config(text="Tour de: —")
    
    def _process_enemy_turn(self):
        """Process enemy turn automatically"""
        current_combatant = self.combat.get_current_combatant()
        
        if current_combatant:
            name, is_player = current_combatant
            
            if not is_player:
                # Find the enemy
                enemy = None
                for e, _ in self.combat.enemies_in_combat:
                    if e.name == name:
                        enemy = e
                        break
                
                if enemy and not enemy.is_defeated():
                    # Enemy attacks a random player
                    if self.combat.combatants:
                        target_char, _ = self.combat.combatants[0]  # Simplified - attack first player
                        
                        # Perform attack
                        result = self.combat.attack(name, target_char.name)
                        self._add_to_log(result)
                        
                        # Update combatants display
                        self._display_combatants()
                        
                        # Check if target is defeated
                        if target_char.current_hp <= 0:
                            self._add_to_log(f"{target_char.name} est inconscient!")
                        
                        # End enemy turn
                        self._end_turn()
    
    def _show_attack_dialog(self):
        """Show attack dialog"""
        current_combatant = self.combat.get_current_combatant()
        
        if not current_combatant:
            return
        
        name, is_player = current_combatant
        
        if not is_player:
            messagebox.showwarning("Tour de l'ennemi", "Ce n'est pas votre tour!")
            return
        
        # Find the character
        character = None
        for char, _ in self.combat.combatants:
            if char.name == name:
                character = char
                break
        
        if not character:
            return
        
        # Create attack dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Attaquer")
        dialog.geometry("400x400")
        dialog.transient(self.window)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"{character.name} attaque", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Target selection
        ttk.Label(main_frame, text="Cible:", font=('Arial', 10)).pack(anchor=tk.W, pady=5)
        
        # List of enemies
        self.target_var = tk.StringVar()
        
        for enemy, _ in self.combat.enemies_in_combat:
            if not enemy.is_defeated():
                rb = ttk.Radiobutton(
                    main_frame,
                    text=f"{enemy.name} ({enemy.current_hp}/{enemy.hit_points} PV)",
                    variable=self.target_var,
                    value=enemy.name
                )
                rb.pack(anchor=tk.W)
        
        # Weapon selection
        ttk.Label(main_frame, text="Arme:", font=('Arial', 10)).pack(anchor=tk.W, pady=(10, 5))
        
        self.weapon_var = tk.StringVar(value="non armé")
        
        # Unarmed option
        rb = ttk.Radiobutton(
            main_frame,
            text="Non armé (1d4 + FOR)",
            variable=self.weapon_var,
            value="non armé"
        )
        rb.pack(anchor=tk.W)
        
        # Character weapons
        for weapon in character.weapons:
            rb = ttk.Radiobutton(
                main_frame,
                text=f"{weapon.name} ({weapon.damage_dice} {weapon.damage_type.value})",
                variable=self.weapon_var,
                value=weapon.name
            )
            rb.pack(anchor=tk.W)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        def perform_attack():
            target_name = self.target_var.get()
            weapon_name = self.weapon_var.get()
            
            if not target_name:
                messagebox.showwarning("Aucune cible", "Veuillez sélectionner une cible")
                return
            
            # Find weapon
            weapon = None
            if weapon_name != "non armé":
                for w in character.weapons:
                    if w.name == weapon_name:
                        weapon = w
                        break
            
            # Perform attack
            result = self.combat.attack(name, target_name, weapon)
            self._add_to_log(result)
            
            # Update combatants display
            self._display_combatants()
            
            # Check if target is defeated
            for enemy, _ in self.combat.enemies_in_combat:
                if enemy.name == target_name and enemy.is_defeated():
                    self._add_to_log(f"{enemy.name} est vaincu!")
            
            dialog.destroy()
        
        ttk.Button(buttons_frame, text="Attaquer", command=perform_attack, style="Combat.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _show_spell_dialog(self):
        """Show spell casting dialog"""
        current_combatant = self.combat.get_current_combatant()
        
        if not current_combatant:
            return
        
        name, is_player = current_combatant
        
        if not is_player:
            messagebox.showwarning("Tour de l'ennemi", "Ce n'est pas votre tour!")
            return
        
        # Find the character
        character = None
        for char, _ in self.combat.combatants:
            if char.name == name:
                character = char
                break
        
        if not character:
            return
        
        # Check if character has spells
        if not character.known_spells:
            messagebox.showinfo("Aucun sort", f"{character.name} ne connaît aucun sort!")
            return
        
        # Create spell dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Lancer un sort")
        dialog.geometry("400x400")
        dialog.transient(self.window)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"{character.name} lance un sort", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Spell selection
        ttk.Label(main_frame, text="Sort:", font=('Arial', 10)).pack(anchor=tk.W, pady=5)
        
        self.spell_var = tk.StringVar()
        
        for spell_name in character.known_spells:
            rb = ttk.Radiobutton(
                main_frame,
                text=spell_name,
                variable=self.spell_var,
                value=spell_name
            )
            rb.pack(anchor=tk.W)
        
        # Target selection (optional)
        ttk.Label(main_frame, text="Cible (optionnel):", font=('Arial', 10)).pack(anchor=tk.W, pady=5)
        
        self.spell_target_var = tk.StringVar(value="")
        
        # List of valid targets (enemies and players)
        targets = []
        for enemy, _ in self.combat.enemies_in_combat:
            if not enemy.is_defeated():
                targets.append(enemy.name)
        for char, _ in self.combat.combatants:
            if char.current_hp > 0:
                targets.append(char.name)
        
        if targets:
            target_menu = ttk.Combobox(
                main_frame,
                textvariable=self.spell_target_var,
                values=targets
            )
            target_menu.pack(fill=tk.X, pady=2)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        def cast_spell():
            spell_name = self.spell_var.get()
            target_name = self.spell_target_var.get()
            
            if not spell_name:
                messagebox.showwarning("Aucun sort", "Veuillez sélectionner un sort")
                return
            
            # Cast the spell
            result = self.combat.cast_spell(name, spell_name, target_name if target_name else None)
            self._add_to_log(result)
            
            dialog.destroy()
        
        ttk.Button(buttons_frame, text="Lancer", command=cast_spell, style="Spell.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _show_item_dialog(self):
        """Show item use dialog"""
        current_combatant = self.combat.get_current_combatant()
        
        if not current_combatant:
            return
        
        name, is_player = current_combatant
        
        if not is_player:
            messagebox.showwarning("Tour de l'ennemi", "Ce n'est pas votre tour!")
            return
        
        # Find the character
        character = None
        for char, _ in self.combat.combatants:
            if char.name == name:
                character = char
                break
        
        if not character:
            return
        
        # Check if character has items
        if not character.inventory:
            messagebox.showinfo("Inventaire vide", f"{character.name} n'a aucun objet!")
            return
        
        # Create item dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Utiliser un objet")
        dialog.geometry("400x400")
        dialog.transient(self.window)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"{character.name} utilise un objet", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Item selection
        ttk.Label(main_frame, text="Objet:", font=('Arial', 10)).pack(anchor=tk.W, pady=5)
        
        self.item_var = tk.StringVar()
        
        for item in character.inventory:
            rb = ttk.Radiobutton(
                main_frame,
                text=item.name,
                variable=self.item_var,
                value=item.name
            )
            rb.pack(anchor=tk.W)
        
        # Target selection (optional)
        ttk.Label(main_frame, text="Cible (optionnel):", font=('Arial', 10)).pack(anchor=tk.W, pady=5)
        
        self.item_target_var = tk.StringVar(value="")
        
        # List of valid targets
        targets = [character.name]  # Can target self
        for enemy, _ in self.combat.enemies_in_combat:
            if not enemy.is_defeated():
                targets.append(enemy.name)
        for char, _ in self.combat.combatants:
            if char.current_hp > 0 and char.name != character.name:
                targets.append(char.name)
        
        target_menu = ttk.Combobox(
            main_frame,
            textvariable=self.item_target_var,
            values=targets
        )
        target_menu.pack(fill=tk.X, pady=2)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        def use_item():
            item_name = self.item_var.get()
            target_name = self.item_target_var.get()
            
            if not item_name:
                messagebox.showwarning("Aucun objet", "Veuillez sélectionner un objet")
                return
            
            # Find and use the item
            item = None
            for i in character.inventory:
                if i.name == item_name:
                    item = i
                    break
            
            if item:
                # For now, just display message
                if target_name:
                    self._add_to_log(f"{character.name} utilise {item.name} sur {target_name}")
                else:
                    self._add_to_log(f"{character.name} utilise {item.name}")
                
                # Remove consumable items
                from models.item import Potion
                if isinstance(item, Potion):
                    character.remove_from_inventory(item)
                    
                    # Apply potion effect
                    if "soins" in item.name.lower():
                        if "supérieurs" in item.name.lower():
                            heal_amount = 10
                        else:
                            heal_amount = 5
                        
                        if target_name == character.name:
                            old_hp = character.current_hp
                            character.heal(heal_amount)
                            self._add_to_log(f"{character.name} récupère {heal_amount} PV ({old_hp} -> {character.current_hp})")
                        else:
                            # Find target character
                            for char, _ in self.combat.combatants:
                                if char.name == target_name:
                                    old_hp = char.current_hp
                                    char.heal(heal_amount)
                                    self._add_to_log(f"{target_name} récupère {heal_amount} PV ({old_hp} -> {char.current_hp})")
                                    break
                    
                    # Update combatants display
                    self._display_combatants()
            
            dialog.destroy()
        
        ttk.Button(buttons_frame, text="Utiliser", command=use_item, style="Item.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _end_turn(self):
        """End current turn"""
        # Move to next turn
        next_turn = self.combat.next_turn()
        
        if next_turn is None:
            # Combat ended
            self._end_combat()
            return
        
        # Update round info
        self.round_label.config(text=f"Round: {self.combat.current_round}")
        
        # Update turn info
        self._update_turn_info()
        
        # Display turn change
        name, is_player = next_turn
        side = "Joueur" if is_player else "Ennemi"
        self._add_to_log(f"Tour de {name} ({side})")
        
        # Update turn order display
        self._display_turn_order()
    
    def _flee_combat(self):
        """Flee from combat"""
        if messagebox.askyesno("Fuir", "Voulez-vous vraiment fuir le combat?"):
            self._add_to_log("Vous fuyez le combat!")
            self._end_combat(fuite=True)
    
    def _end_combat(self, fuite: bool = False):
        """End the combat"""
        if fuite:
            result = "Vous avez fui le combat!"
        else:
            # Check who won
            all_enemies_defeated = all(enemy.is_defeated() for enemy, _ in self.combat.enemies_in_combat)
            all_players_defeated = all(char.current_hp <= 0 for char, _ in self.combat.combatants)
            
            if all_enemies_defeated:
                result = "Victoire! Tous les ennemis ont été vaincus!"
            elif all_players_defeated:
                result = "Défaite! Tous les personnages sont inconscients!"
            else:
                result = "Combat terminé."
        
        # Close window
        self._on_window_close()
        
        # Notify parent
        self.on_combat_end(result)
    
    def _add_to_log(self, text: str):
        """Add text to combat log"""
        self.combat_log.config(state=tk.NORMAL)
        self.combat_log.insert(tk.END, f"{text}\n")
        self.combat_log.config(state=tk.DISABLED)
        self.combat_log.see(tk.END)
    
    def _on_window_close(self):
        """Handle window close"""
        self.window.destroy()
    
    def show(self):
        """Show the window"""
        self.window.deiconify()
        self.window.lift()
    
    def hide(self):
        """Hide the window"""
        self.window.withdraw()


# Import for type hints
from models.combat import Combat
from models.character import Character
