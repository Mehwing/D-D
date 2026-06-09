"""
Dice roller window for D&D application
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from models.dice import Dice, DiceResult, roll_dice, roll_advantage, roll_disadvantage


class DiceRollerWindow:
    """Window for rolling dice"""
    
    def __init__(self, root: tk.Tk, on_roll: Callable[[DiceResult], None], on_close: Callable[[], None]):
        """
        Initialize the dice roller window
        
        Args:
            root: Tkinter root window
            on_roll: Callback when a die is rolled
            on_close: Callback when window is closed
        """
        self.root = root
        self.on_roll = on_roll
        self.on_close = on_close
        
        # Create top-level window
        self.window = tk.Toplevel(root)
        self.window.title("Lanceur de Dés")
        self.window.geometry("400x500")
        self.window.minsize(350, 450)
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
            text="Lanceur de Dés",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        # Dice selection frame
        dice_frame = ttk.LabelFrame(self.main_frame, text="Sélection du Dé", padding="10")
        dice_frame.pack(fill=tk.X, pady=10)
        
        # Dice buttons
        dice_types = [
            ('d4', 'Tétraèdre'),
            ('d6', 'Cube'),
            ('d8', 'Octaèdre'),
            ('d10', 'Décagone'),
            ('d12', 'Dodécaèdre'),
            ('d20', 'Icosaèdre'),
            ('d100', 'Centaine'),
        ]
        
        for dice_type, dice_name in dice_types:
            btn = ttk.Button(
                dice_frame,
                text=f"{dice_name} ({dice_type})",
                command=lambda dt=dice_type: self._roll_dice(dt),
                style="Dice.TButton"
            )
            btn.pack(fill=tk.X, pady=2)
        
        # Custom dice frame
        custom_frame = ttk.LabelFrame(self.main_frame, text="Dé Personnalisé", padding="10")
        custom_frame.pack(fill=tk.X, pady=10)
        
        # Custom dice entry
        self.custom_dice_var = tk.StringVar(value="1d20")
        custom_entry = ttk.Entry(
            custom_frame,
            textvariable=self.custom_dice_var,
            font=('Arial', 10)
        )
        custom_entry.pack(fill=tk.X, pady=5)
        
        # Roll custom button
        custom_button = ttk.Button(
            custom_frame,
            text="Lancer",
            command=self._roll_custom_dice,
            style="Accent.TButton"
        )
        custom_button.pack(fill=tk.X)
        
        # Modifier frame
        mod_frame = ttk.LabelFrame(self.main_frame, text="Modificateur", padding="10")
        mod_frame.pack(fill=tk.X, pady=10)
        
        # Modifier entry
        self.modifier_var = tk.IntVar(value=0)
        mod_entry = ttk.Entry(
            mod_frame,
            textvariable=self.modifier_var,
            font=('Arial', 10)
        )
        mod_entry.pack(fill=tk.X, pady=5)
        
        # Advantage/disadvantage buttons
        adv_frame = ttk.Frame(mod_frame)
        adv_frame.pack(fill=tk.X)
        
        ttk.Button(
            adv_frame,
            text="Avantage",
            command=self._roll_advantage,
            style="Advantage.TButton"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        ttk.Button(
            adv_frame,
            text="Désavantage",
            command=self._roll_disadvantage,
            style="Disadvantage.TButton"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Result frame
        result_frame = ttk.LabelFrame(self.main_frame, text="Résultat", padding="10")
        result_frame.pack(fill=tk.X, pady=10)
        
        # Result display
        self.result_label = ttk.Label(
            result_frame,
            text="Aucun jet effectué",
            font=('Arial', 12),
            wraplength=350
        )
        self.result_label.pack(fill=tk.X, pady=10)
        
        # History frame
        history_frame = ttk.LabelFrame(self.main_frame, text="Historique", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # History text
        self.history_text = tk.Text(
            history_frame,
            wrap=tk.WORD,
            font=('Arial', 9),
            state=tk.DISABLED,
            height=6
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for history
        scrollbar = ttk.Scrollbar(history_frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
        
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
        
        # Dice button style
        style.configure(
            "Dice.TButton",
            foreground="white",
            background="#4682B4",  # Steel blue
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Dice.TButton",
            background=[("active", "#5A9BD5"), ("disabled", "#284768")]
        )
        
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
        
        # Advantage button style
        style.configure(
            "Advantage.TButton",
            foreground="white",
            background="#2E8B57",  # Sea green
            font=('Arial', 9, 'bold'),
            padding=3
        )
        style.map(
            "Advantage.TButton",
            background=[("active", "#3CB371"), ("disabled", "#1E5B39")]
        )
        
        # Disadvantage button style
        style.configure(
            "Disadvantage.TButton",
            foreground="white",
            background="#8B0000",  # Dark red
            font=('Arial', 9, 'bold'),
            padding=3
        )
        style.map(
            "Disadvantage.TButton",
            background=[("active", "#A00000"), ("disabled", "#400000")]
        )
        
        # Frame styling
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
    
    def _roll_dice(self, dice_type: str):
        """Roll a specific dice type"""
        modifier = self.modifier_var.get()
        result = Dice.roll(dice_type, 1, modifier)
        self._display_result(result, f"{dice_type}")
    
    def _roll_custom_dice(self):
        """Roll custom dice notation"""
        notation = self.custom_dice_var.get()
        modifier = self.modifier_var.get()
        
        try:
            # Add modifier to notation if present
            if modifier != 0:
                if '+' in notation or '-' in notation:
                    # Already has modifier
                    result = roll_dice(notation)
                else:
                    # Add modifier
                    result = roll_dice(f"{notation}+{modifier}" if modifier > 0 else f"{notation}{modifier}")
            else:
                result = roll_dice(notation)
            
            self._display_result(result, notation)
        except Exception as e:
            self.result_label.config(text=f"Erreur: {e}")
    
    def _roll_advantage(self):
        """Roll with advantage"""
        dice_type = self.custom_dice_var.get().lower()
        modifier = self.modifier_var.get()
        
        # Default to d20 if not specified
        if not dice_type.startswith('d'):
            dice_type = 'd20'
        
        try:
            result, roll1, roll2 = roll_advantage(dice_type, modifier)
            self._display_result(result, f"{dice_type} (avantage)")
            
            # Show both rolls in history
            self._add_to_history(f"Avantage: {roll1.value} et {roll2.value} -> {result.value}")
        except Exception as e:
            self.result_label.config(text=f"Erreur: {e}")
    
    def _roll_disadvantage(self):
        """Roll with disadvantage"""
        dice_type = self.custom_dice_var.get().lower()
        modifier = self.modifier_var.get()
        
        # Default to d20 if not specified
        if not dice_type.startswith('d'):
            dice_type = 'd20'
        
        try:
            result, roll1, roll2 = roll_disadvantage(dice_type, modifier)
            self._display_result(result, f"{dice_type} (désavantage)")
            
            # Show both rolls in history
            self._add_to_history(f"Désavantage: {roll1.value} et {roll2.value} -> {result.value}")
        except Exception as e:
            self.result_label.config(text=f"Erreur: {e}")
    
    def _display_result(self, result: DiceResult, notation: str):
        """Display the roll result"""
        # Build result text
        result_text = f"{notation}: {result.value}"
        
        if result.is_critical:
            result_text += " (Critique!)"
        elif result.is_fumble:
            result_text += " (Fumble!)"
        
        self.result_label.config(text=result_text)
        
        # Add to history
        self._add_to_history(result_text)
        
        # Notify parent
        self.on_roll(result)
    
    def _add_to_history(self, text: str):
        """Add entry to history"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"{text}\n")
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
    
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
from models.dice import DiceResult
