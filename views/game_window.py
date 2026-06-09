"""
Main game window for D&D application
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Dict, Optional, Callable
import threading
import time

from models.scenario import Scenario, ScenarioEvent, ScenarioEventType, ScenarioChoice
from models.character import Character
from models.combat import Combat
from models.dice import Dice, DiceResult, roll_dice
from models.item import Item, Weapon, Armor, Potion
from models.spell import Spell, get_spell_by_name

from .character_sheet_window import CharacterSheetWindow
from .dice_roller_window import DiceRollerWindow
from .inventory_window import InventoryWindow
from .combat_window import CombatWindow


class GameWindow:
    """Main game window for playing D&D scenarios"""
    
    def __init__(self, root: tk.Tk, scenario: Scenario, characters: List[Character], on_quit: Callable[[], None]):
        """
        Initialize the game window
        
        Args:
            root: Tkinter root window
            scenario: The scenario to play
            characters: List of player characters
            on_quit: Callback when quitting to main menu
        """
        self.root = root
        self.scenario = scenario
        self.characters = characters
        self.on_quit = on_quit
        self.game_state: Dict = {
            'characters': self.characters,
            'variables': {},
            'current_combat': None,
            'combat_started': False
        }
        
        # Configure root window
        self.root.title(f"Donjons & Dragons - {scenario.title}")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set window icon
        try:
            self.root.iconbitmap(default='dnd_icon.ico')
        except:
            pass
        
        # Create main container
        self.main_container = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel (character profiles)
        self.left_panel = ttk.Frame(self.main_container, width=300, padding="10")
        self.main_container.add(self.left_panel, width=300)
        
        # Create right panel (main content)
        self.right_panel = ttk.Frame(self.main_container, padding="10")
        self.main_container.add(self.right_panel)
        
        # Create UI
        self._create_left_panel()
        self._create_right_panel()
        
        # Start the scenario
        self.scenario.start()
        self._display_current_event()
        
        # Configure styles
        self._configure_styles()
        
        # Child windows
        self.character_sheet_window: Optional[CharacterSheetWindow] = None
        self.dice_roller_window: Optional[DiceRollerWindow] = None
        self.inventory_window: Optional[InventoryWindow] = None
        self.combat_window: Optional[CombatWindow] = None
    
    def _create_left_panel(self):
        """Create the left panel with character profiles"""
        # Title
        title_label = ttk.Label(
            self.left_panel,
            text="Personnages",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(fill=tk.X, pady=5)
        
        # Character list frame
        char_list_frame = ttk.Frame(self.left_panel)
        char_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Character tabs
        self.char_tabs = ttk.Notebook(char_list_frame)
        self.char_tabs.pack(fill=tk.BOTH, expand=True)
        
        # Create a tab for each character
        for char in self.characters:
            self._create_character_tab(char)
        
        # Add buttons frame
        buttons_frame = ttk.Frame(self.left_panel)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        # Character sheet button
        sheet_button = ttk.Button(
            buttons_frame,
            text="Fiche Complète",
            command=self._show_character_sheet
        )
        sheet_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Inventory button
        inv_button = ttk.Button(
            buttons_frame,
            text="Inventaire",
            command=self._show_inventory
        )
        inv_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Dice roller button
        dice_button = ttk.Button(
            buttons_frame,
            text="Lancer de Dés",
            command=self._show_dice_roller
        )
        dice_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
    
    def _create_character_tab(self, character: Character):
        """Create a tab for a character"""
        tab = ttk.Frame(self.char_tabs)
        self.char_tabs.add(tab, text=character.name)
        
        # Character portrait (placeholder)
        portrait_frame = ttk.Frame(tab, height=80, width=80)
        portrait_frame.pack(pady=5)
        portrait_frame.pack_propagate(False)
        
        # Use a colored canvas as placeholder
        portrait_canvas = tk.Canvas(portrait_frame, bg="#8B4513", highlightthickness=0)
        portrait_canvas.pack(fill=tk.BOTH, expand=True)
        portrait_canvas.create_text(
            40, 40,
            text=character.race.value[0] + character.char_class.value[0],
            fill="white",
            font=('Arial', 24, 'bold')
        )
        
        # Character info
        info_frame = ttk.Frame(tab)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Basic info
        ttk.Label(info_frame, text=f"{character.race.value} {character.char_class.value}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Niveau {character.level}", font=('Arial', 9)).pack(anchor=tk.W)
        
        # Health bar
        health_frame = ttk.Frame(tab)
        health_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(health_frame, text=f"PV: {character.current_hp}/{character.max_hp}", font=('Arial', 9)).pack(anchor=tk.W)
        
        # Health bar visualization
        health_canvas = tk.Canvas(health_frame, height=10, bg="#ccc")
        health_canvas.pack(fill=tk.X, pady=2)
        
        # Draw health bar
        health_percent = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        bar_width = 100
        health_canvas.create_rectangle(
            0, 0, bar_width * health_percent, 10,
            fill="#4CAF50" if health_percent > 0.5 else "#FFC107" if health_percent > 0.25 else "#F44336",
            outline=""
        )
        
        # Stats
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(fill=tk.X, pady=5)
        
        stats = [
            ("FOR", character.stats.strength, character.stats.strength_modifier),
            ("DEX", character.stats.dexterity, character.stats.dexterity_modifier),
            ("CON", character.stats.constitution, character.stats.constitution_modifier),
            ("INT", character.stats.intelligence, character.stats.intelligence_modifier),
            ("SAG", character.stats.wisdom, character.stats.wisdom_modifier),
            ("CHA", character.stats.charisma, character.stats.charisma_modifier),
        ]
        
        for stat_name, stat_value, modifier in stats:
            stat_label = ttk.Label(
                stats_frame,
                text=f"{stat_name}: {stat_value} ({modifier:+d})",
                font=('Arial', 8)
            )
            stat_label.pack(anchor=tk.W)
        
        # AC and other info
        ttk.Label(tab, text=f"CA: {character.armor_class}", font=('Arial', 9)).pack(anchor=tk.W)
        ttk.Label(tab, text=f"Or: {character.gold} po", font=('Arial', 9)).pack(anchor=tk.W)
        
        # Update tab when character changes
        def update_tab():
            # Update health
            health_percent = character.current_hp / character.max_hp if character.max_hp > 0 else 0
            health_canvas.delete("all")
            health_canvas.create_rectangle(
                0, 0, bar_width * health_percent, 10,
                fill="#4CAF50" if health_percent > 0.5 else "#FFC107" if health_percent > 0.25 else "#F44336",
                outline=""
            )
            
            # Update labels
            for widget in tab.winfo_children():
                if isinstance(widget, ttk.Label):
                    widget.destroy()
            
            self._create_character_tab(character)
        
        # This is a simplified approach - in a real app, we'd have a better way to update
    
    def _create_right_panel(self):
        """Create the right panel with scenario content"""
        # Main content frame
        self.content_frame = ttk.Frame(self.right_panel)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scenario title
        self.title_label = ttk.Label(
            self.content_frame,
            text=self.scenario.title,
            font=('Arial', 16, 'bold')
        )
        self.title_label.pack(fill=tk.X, pady=5)
        
        # Event title
        self.event_title_label = ttk.Label(
            self.content_frame,
            text="",
            font=('Arial', 12, 'bold')
        )
        self.event_title_label.pack(fill=tk.X, pady=5)
        
        # Scrollable text area for scenario content
        text_frame = ttk.Frame(self.content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.scenario_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            padx=10,
            pady=10,
            state=tk.DISABLED,
            bg="#f8f8f8"
        )
        self.scenario_text.pack(fill=tk.BOTH, expand=True)
        
        # Choices frame
        self.choices_frame = ttk.Frame(self.content_frame)
        self.choices_frame.pack(fill=tk.X, pady=10)
        
        # Action buttons frame
        self.action_buttons_frame = ttk.Frame(self.content_frame)
        self.action_buttons_frame.pack(fill=tk.X, pady=5)
        
        # Continue button
        self.continue_button = ttk.Button(
            self.action_buttons_frame,
            text="Continuer",
            command=self._continue_scenario,
            style="Accent.TButton"
        )
        self.continue_button.pack(side=tk.LEFT, padx=5)
        
        # Quit button
        quit_button = ttk.Button(
            self.action_buttons_frame,
            text="Quitter",
            command=self._quit_game
        )
        quit_button.pack(side=tk.RIGHT, padx=5)
        
        # Combat button (shown when in combat)
        self.combat_button = ttk.Button(
            self.action_buttons_frame,
            text="Combattre",
            command=self._start_combat,
            style="Combat.TButton"
        )
        
        # Save button
        save_button = ttk.Button(
            self.action_buttons_frame,
            text="Sauvegarder",
            command=self._save_game
        )
        save_button.pack(side=tk.RIGHT, padx=5)
    
    def _configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        
        # Accent button style
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#8B0000",  # Dark red
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#A00000"), ("disabled", "#400000")]
        )
        
        # Combat button style
        style.configure(
            "Combat.TButton",
            foreground="white",
            background="#8B0000",
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Combat.TButton",
            background=[("active", "#FF0000"), ("disabled", "#600000")]
        )
        
        # Frame styling
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
    
    def _display_current_event(self):
        """Display the current scenario event"""
        current_event = self.scenario.get_current_event()
        
        if not current_event:
            self._show_end_screen()
            return
        
        # Update event title
        self.event_title_label.config(text=current_event.title if current_event.title else "")
        
        # Clear previous choices
        for widget in self.choices_frame.winfo_children():
            widget.destroy()
        
        # Clear previous text
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.delete(1.0, tk.END)
        
        # Display event text
        if current_event.text:
            self.scenario_text.insert(tk.END, current_event.text + "\n\n")
        
        # Handle different event types
        if current_event.event_type == ScenarioEventType.CHOICE:
            self._display_choices(current_event)
            self.continue_button.pack_forget()
        elif current_event.event_type == ScenarioEventType.COMBAT:
            self._handle_combat_event(current_event)
        elif current_event.event_type == ScenarioEventType.CHECK:
            self._handle_check_event(current_event)
        elif current_event.event_type == ScenarioEventType.TRAP:
            self._handle_trap_event(current_event)
        else:
            # For text, dialogue, reward, rest, end events
            self.continue_button.pack(side=tk.LEFT, padx=5)
            
            # If there's a combat in progress, show combat button
            if self.game_state.get('current_combat') and not self.game_state.get('combat_started'):
                self.combat_button.pack(side=tk.LEFT, padx=5)
            else:
                self.combat_button.pack_forget()
        
        self.scenario_text.config(state=tk.DISABLED)
        self.scenario_text.see(tk.END)
    
    def _display_choices(self, event: ScenarioEvent):
        """Display choices for the player"""
        available_choices = self.scenario.get_available_choices(self.game_state)
        
        if not available_choices:
            available_choices = event.choices
        
        for i, choice in enumerate(available_choices):
            choice_button = ttk.Button(
                self.choices_frame,
                text=choice.text,
                command=lambda idx=i: self._select_choice(idx),
                style="Accent.TButton"
            )
            choice_button.pack(fill=tk.X, pady=2)
    
    def _select_choice(self, choice_index: int):
        """Handle player choice selection"""
        current_event = self.scenario.get_current_event()
        if not current_event:
            return
        
        # Execute the event with the chosen index
        result_text, next_event_id = self.scenario.next_event(self.game_state, choice_index)
        
        # Display result
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.insert(tk.END, f"\n{result_text}\n\n")
        self.scenario_text.config(state=tk.DISABLED)
        self.scenario_text.see(tk.END)
        
        # Clear choices
        for widget in self.choices_frame.winfo_children():
            widget.destroy()
        
        # Check if we need to start combat
        if self.game_state.get('current_combat') and not self.game_state.get('combat_started'):
            self._start_combat()
        else:
            # Continue to next event
            self._display_current_event()
    
    def _continue_scenario(self):
        """Continue to the next event"""
        current_event = self.scenario.get_current_event()
        if not current_event:
            return
        
        # Execute the event without a choice
        result_text, next_event_id = self.scenario.next_event(self.game_state, -1)
        
        # Display result
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.insert(tk.END, f"\n{result_text}\n\n")
        self.scenario_text.config(state=tk.DISABLED)
        self.scenario_text.see(tk.END)
        
        # Check if we need to start combat
        if self.game_state.get('current_combat') and not self.game_state.get('combat_started'):
            self._start_combat()
        else:
            # Continue to next event
            self._display_current_event()
    
    def _handle_combat_event(self, event: ScenarioEvent):
        """Handle combat event"""
        # Display combat description
        self.scenario_text.config(state=tk.NORMAL)
        
        if event.combat_name:
            combat = self.game_state.get('current_combat')
            if combat:
                self.scenario_text.insert(tk.END, f"{combat.description}\n\n")
        elif event.enemy_names:
            enemies = ", ".join(event.enemy_names)
            self.scenario_text.insert(tk.END, f"{enemies} apparaissent!\n\n")
        
        self.scenario_text.config(state=tk.DISABLED)
        
        # Show combat button
        self.combat_button.pack(side=tk.LEFT, padx=5)
        self.continue_button.pack_forget()
    
    def _handle_check_event(self, event: ScenarioEvent):
        """Handle skill check event"""
        # For now, just continue - the check will be handled in next_event
        self.continue_button.pack(side=tk.LEFT, padx=5)
    
    def _handle_trap_event(self, event: ScenarioEvent):
        """Handle trap event"""
        # For now, just continue - the trap logic will be handled in next_event
        self.continue_button.pack(side=tk.LEFT, padx=5)
    
    def _start_combat(self):
        """Start combat encounter"""
        combat = self.game_state.get('current_combat')
        if not combat:
            return
        
        # Start the combat
        combat.start_combat(self.characters)
        self.game_state['combat_started'] = True
        
        # Open combat window
        self.combat_window = CombatWindow(
            self.root,
            combat,
            self.characters,
            on_combat_end=self._on_combat_end
        )
        
        # Hide combat button
        self.combat_button.pack_forget()
    
    def _on_combat_end(self, combat_result: str):
        """Handle combat end"""
        self.game_state['current_combat'] = None
        self.game_state['combat_started'] = False
        
        # Display combat result
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.insert(tk.END, f"\n{combat_result}\n\n")
        self.scenario_text.config(state=tk.DISABLED)
        self.scenario_text.see(tk.END)
        
        # Continue scenario
        self._display_current_event()
    
    def _show_end_screen(self):
        """Show end screen"""
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.delete(1.0, tk.END)
        self.scenario_text.insert(tk.END, "Fin du scénario!\n\n")
        self.scenario_text.insert(tk.END, "Merci d'avoir joué!\n")
        self.scenario_text.config(state=tk.DISABLED)
        
        # Hide continue button
        self.continue_button.pack_forget()
        self.combat_button.pack_forget()
    
    def _show_character_sheet(self):
        """Show character sheet for selected character"""
        # Get selected character from tabs
        current_tab = self.char_tabs.index(self.char_tabs.select())
        if current_tab < len(self.characters):
            character = self.characters[current_tab]
            
            if not self.character_sheet_window:
                self.character_sheet_window = CharacterSheetWindow(
                    self.root,
                    character,
                    on_close=self._on_character_sheet_close
                )
            else:
                self.character_sheet_window.update_character(character)
                self.character_sheet_window.show()
    
    def _on_character_sheet_close(self):
        """Handle character sheet window close"""
        self.character_sheet_window = None
    
    def _show_inventory(self):
        """Show inventory for selected character"""
        current_tab = self.char_tabs.index(self.char_tabs.select())
        if current_tab < len(self.characters):
            character = self.characters[current_tab]
            
            if not self.inventory_window:
                self.inventory_window = InventoryWindow(
                    self.root,
                    character,
                    on_close=self._on_inventory_close
                )
            else:
                self.inventory_window.update_character(character)
                self.inventory_window.show()
    
    def _on_inventory_close(self):
        """Handle inventory window close"""
        self.inventory_window = None
    
    def _show_dice_roller(self):
        """Show dice roller window"""
        if not self.dice_roller_window:
            self.dice_roller_window = DiceRollerWindow(
                self.root,
                on_roll=self._on_dice_roll,
                on_close=self._on_dice_roller_close
            )
        else:
            self.dice_roller_window.show()
    
    def _on_dice_roll(self, result: DiceResult):
        """Handle dice roll result"""
        # Display roll result in scenario text
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.insert(tk.END, f"\n[Jet de dé: {result.dice_type} = {result.value}]\n")
        self.scenario_text.config(state=tk.DISABLED)
        self.scenario_text.see(tk.END)
    
    def _on_dice_roller_close(self):
        """Handle dice roller window close"""
        self.dice_roller_window = None
    
    def _save_game(self):
        """Save game state"""
        messagebox.showinfo("Sauvegarde", "Fonctionnalité de sauvegarde à venir!")
    
    def _quit_game(self):
        """Quit game and return to main menu"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter la partie en cours?"):
            self.on_quit()
    
    def update_character_tabs(self):
        """Update all character tabs"""
        # Recreate all tabs
        for tab in self.char_tabs.winfo_children():
            self.char_tabs.forget(tab)
        
        for char in self.characters:
            self._create_character_tab(char)


# Import for type hints
from models.scenario import Scenario
from models.character import Character
