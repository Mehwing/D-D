"""
Inventory window for D&D application
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable

from models.character import Character
from models.item import Item, Weapon, Armor, Potion, get_item_by_name


class InventoryWindow:
    """Window for viewing and managing character inventory"""
    
    def __init__(self, root: tk.Tk, character: Character, on_close: Callable[[], None]):
        """
        Initialize the inventory window
        
        Args:
            root: Tkinter root window
            character: The character whose inventory to display
            on_close: Callback when window is closed
        """
        self.root = root
        self.character = character
        self.on_close = on_close
        
        # Create top-level window
        self.window = tk.Toplevel(root)
        self.window.title(f"Inventaire - {character.name}")
        self.window.geometry("600x500")
        self.window.minsize(500, 400)
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
            text=f"Inventaire de {self.character.name}",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=5)
        
        # Character info frame
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Gold display
        gold_label = ttk.Label(
            info_frame,
            text=f"Or: {self.character.gold} pièces",
            font=('Arial', 10)
        )
        gold_label.pack(side=tk.LEFT, padx=10)
        
        # Weight display (placeholder)
        weight_label = ttk.Label(
            info_frame,
            text="Poids: —",
            font=('Arial', 10)
        )
        weight_label.pack(side=tk.RIGHT, padx=10)
        
        # Inventory tabs
        self.inventory_tabs = ttk.Notebook(self.main_frame)
        self.inventory_tabs.pack(fill=tk.BOTH, expand=True)
        
        # All items tab
        self.all_items_frame = ttk.Frame(self.inventory_tabs)
        self.inventory_tabs.add(self.all_items_frame, text="Tous les objets")
        
        # Weapons tab
        self.weapons_frame = ttk.Frame(self.inventory_tabs)
        self.inventory_tabs.add(self.weapons_frame, text="Armes")
        
        # Armor tab
        self.armor_frame = ttk.Frame(self.inventory_tabs)
        self.inventory_tabs.add(self.armor_frame, text="Armures")
        
        # Potions tab
        self.potions_frame = ttk.Frame(self.inventory_tabs)
        self.inventory_tabs.add(self.potions_frame, text="Potions")
        
        # Misc tab
        self.misc_frame = ttk.Frame(self.inventory_tabs)
        self.inventory_tabs.add(self.misc_frame, text="Divers")
        
        # Populate tabs
        self._populate_tabs()
        
        # Action buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Add item button
        add_button = ttk.Button(
            buttons_frame,
            text="Ajouter un objet",
            command=self._add_item,
            style="Accent.TButton"
        )
        add_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Remove item button
        remove_button = ttk.Button(
            buttons_frame,
            text="Retirer un objet",
            command=self._remove_item,
            style="Remove.TButton"
        )
        remove_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Use item button
        use_button = ttk.Button(
            buttons_frame,
            text="Utiliser un objet",
            command=self._use_item,
            style="Use.TButton"
        )
        use_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Close button
        close_button = ttk.Button(
            self.main_frame,
            text="Fermer",
            command=self._on_window_close
        )
        close_button.pack(pady=5)
    
    def _configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        
        # Accent button style
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#2E8B57",  # Sea green
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#3CB371"), ("disabled", "#1E5B39")]
        )
        
        # Remove button style
        style.configure(
            "Remove.TButton",
            foreground="white",
            background="#8B0000",  # Dark red
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Remove.TButton",
            background=[("active", "#A00000"), ("disabled", "#400000")]
        )
        
        # Use button style
        style.configure(
            "Use.TButton",
            foreground="white",
            background="#4682B4",  # Steel blue
            font=('Arial', 10, 'bold'),
            padding=5
        )
        style.map(
            "Use.TButton",
            background=[("active", "#5A9BD5"), ("disabled", "#284768")]
        )
        
        # Frame styling
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
    
    def _populate_tabs(self):
        """Populate the inventory tabs with items"""
        # Clear existing items
        for frame in [self.all_items_frame, self.weapons_frame, self.armor_frame, 
                      self.potions_frame, self.misc_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
        
        # Categorize items
        weapons = []
        armors = []
        potions = []
        misc = []
        
        for item in self.character.inventory:
            if isinstance(item, Weapon):
                weapons.append(item)
            elif isinstance(item, Armor):
                armors.append(item)
            elif isinstance(item, Potion):
                potions.append(item)
            else:
                misc.append(item)
        
        # Display all items
        self._display_items(self.all_items_frame, self.character.inventory)
        
        # Display categorized items
        self._display_items(self.weapons_frame, weapons)
        self._display_items(self.armor_frame, armors)
        self._display_items(self.potions_frame, potions)
        self._display_items(self.misc_frame, misc)
    
    def _display_items(self, frame: ttk.Frame, items: List[Item]):
        """Display items in a frame"""
        if not items:
            no_items_label = ttk.Label(
                frame,
                text="Aucun objet",
                font=('Arial', 10, 'italic'),
                foreground="gray"
            )
            no_items_label.pack(pady=20)
            return
        
        # Create a canvas with scrollbar for items
        canvas = tk.Canvas(frame, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display each item
        for i, item in enumerate(items):
            item_frame = ttk.Frame(scrollable_frame, padding="5")
            item_frame.pack(fill=tk.X, pady=2)
            
            # Item icon (placeholder)
            icon_frame = ttk.Frame(item_frame, width=30, height=30)
            icon_frame.pack(side=tk.LEFT, padx=5)
            icon_frame.pack_propagate(False)
            
            icon_canvas = tk.Canvas(icon_frame, bg="#8B4513", highlightthickness=0)
            icon_canvas.pack(fill=tk.BOTH, expand=True)
            icon_canvas.create_text(
                15, 15,
                text=item.name[0].upper(),
                fill="white",
                font=('Arial', 12, 'bold')
            )
            
            # Item info
            info_frame = ttk.Frame(item_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            name_label = ttk.Label(
                info_frame,
                text=item.name,
                font=('Arial', 10, 'bold')
            )
            name_label.pack(anchor=tk.W)
            
            type_label = ttk.Label(
                info_frame,
                text=item.item_type.value,
                font=('Arial', 8),
                foreground="gray"
            )
            type_label.pack(anchor=tk.W)
            
            # For weapons and armor, show additional info
            if isinstance(item, Weapon):
                damage_label = ttk.Label(
                    info_frame,
                    text=f"Dégâts: {item.damage_dice} {item.damage_type.value}",
                    font=('Arial', 8)
                )
                damage_label.pack(anchor=tk.W)
            elif isinstance(item, Armor):
                ac_label = ttk.Label(
                    info_frame,
                    text=f"CA: {item.armor_class}",
                    font=('Arial', 8)
                )
                ac_label.pack(anchor=tk.W)
            
            # Item value
            if item.value > 0:
                value_label = ttk.Label(
                    info_frame,
                    text=f"Valeur: {item.value} po",
                    font=('Arial', 8)
                )
                value_label.pack(anchor=tk.W)
            
            # Selection checkbox
            self.item_vars = {}
            item_var = tk.BooleanVar()
            self.item_vars[item.name] = item_var
            
            checkbox = ttk.Checkbutton(
                item_frame,
                variable=item_var
            )
            checkbox.pack(side=tk.RIGHT, padx=5)
    
    def _add_item(self):
        """Add an item to inventory"""
        # Create a dialog to select item
        dialog = tk.Toplevel(self.window)
        dialog.title("Ajouter un objet")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Item selection
        ttk.Label(main_frame, text="Sélectionner un objet:", font=('Arial', 10)).pack(pady=5)
        
        # List of available items
        available_items = [
            "dague", "épée courte", "épée longue", "hache de guerre",
            "arc court", "arc long", "fléchette", "massue", "bâton",
            "armure de cuir", "armure de cuir clouté", "cotte de mailles",
            "armure de plaques", "bouclier",
            "potion de soins", "potion de soins supérieurs", "potion de force",
            "potion de dextérité",
            "corde", "torche", "lanterne", "huile", "ration", "sac à composantes"
        ]
        
        item_listbox = tk.Listbox(main_frame, font=('Arial', 10))
        for item_name in available_items:
            item_listbox.insert(tk.END, item_name)
        item_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        def add_selected_item():
            selected = item_listbox.curselection()
            if selected:
                item_name = available_items[selected[0]]
                item = get_item_by_name(item_name)
                if item:
                    self.character.add_to_inventory(item)
                    self._populate_tabs()
                    dialog.destroy()
        
        ttk.Button(buttons_frame, text="Ajouter", command=add_selected_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _remove_item(self):
        """Remove selected items from inventory"""
        # Find selected items
        selected_items = []
        for item in self.character.inventory:
            if item.name in self.item_vars and self.item_vars[item.name].get():
                selected_items.append(item)
        
        if not selected_items:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner au moins un objet à retirer")
            return
        
        # Confirm removal
        item_names = ", ".join(item.name for item in selected_items)
        if messagebox.askyesno("Retirer", f"Voulez-vous vraiment retirer: {item_names}?"):
            for item in selected_items:
                self.character.remove_from_inventory(item)
            self._populate_tabs()
    
    def _use_item(self):
        """Use selected item"""
        # Find selected items
        selected_items = []
        for item in self.character.inventory:
            if item.name in self.item_vars and self.item_vars[item.name].get():
                selected_items.append(item)
        
        if not selected_items:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un objet à utiliser")
            return
        
        if len(selected_items) > 1:
            messagebox.showwarning("Sélection multiple", "Veuillez sélectionner un seul objet")
            return
        
        item = selected_items[0]
        
        if isinstance(item, Potion):
            # Use potion
            if "soins" in item.name.lower():
                # Healing potion
                if "supérieurs" in item.name.lower():
                    heal_amount = 10  # Simplified
                else:
                    heal_amount = 5  # Simplified
                
                old_hp = self.character.current_hp
                self.character.heal(heal_amount)
                messagebox.showinfo(
                    "Potion utilisée",
                    f"Vous utilisez {item.name} et récupérez {heal_amount} PV ({old_hp} -> {self.character.current_hp})"
                )
                self.character.remove_from_inventory(item)
                self._populate_tabs()
            else:
                messagebox.showinfo("Potion", f"Vous utilisez {item.name}. Effet: {item.effect}")
        else:
            messagebox.showinfo("Objet", f"Vous utilisez {item.name}")
    
    def update_character(self, character: Character):
        """Update the character being displayed"""
        self.character = character
        self.window.title(f"Inventaire - {character.name}")
        self._populate_tabs()
    
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
from models.item import Item
