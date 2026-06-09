"""
Item system for D&D
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ItemType(Enum):
    """Types of items"""
    WEAPON = "Arme"
    ARMOR = "Armure"
    POTION = "Potion"
    SCROLL = "Parchemin"
    FOOD = "Nourriture"
    TOOL = "Outil"
    MISC = "Divers"


class WeaponType(Enum):
    """Types of weapons"""
    SIMPLE_MELEE = "Arme de mêlée simple"
    MARTIAL_MELEE = "Arme de mêlée de guerre"
    SIMPLE_RANGED = "Arme à distance simple"
    MARTIAL_RANGED = "Arme à distance de guerre"


class ArmorType(Enum):
    """Types of armor"""
    LIGHT = "Légère"
    MEDIUM = "Moyenne"
    HEAVY = "Lourde"
    SHIELD = "Bouclier"


class DamageType(Enum):
    """Types of damage"""
    SLASHING = "Tranchant"
    PIERCING = "Perforant"
    BLUDGEONING = "Contondant"
    FIRE = "Feu"
    COLD = "Froid"
    LIGHTNING = "Foudre"
    ACID = "Acide"
    POISON = "Poison"
    NECROTIC = "Nécrotique"
    RADIANT = "Radiant"
    PSYCHIC = "Psychique"
    THUNDER = "Tonnerre"
    FORCE = "Force"


@dataclass
class Item:
    """Base item class"""
    name: str
    item_type: ItemType
    description: str = ""
    weight: float = 0.0  # in pounds
    value: int = 0  # in gold pieces
    
    def __str__(self) -> str:
        return f"{self.name} ({self.item_type.value})"


@dataclass
class Weapon:
    """Weapon class"""
    name: str
    weapon_type: WeaponType = WeaponType.SIMPLE_MELEE
    damage_dice: str = "d6"
    damage_type: DamageType = DamageType.SLASHING
    range: Tuple[int, int] = (5, 0)  # (normal, long) in feet, 0 for melee
    properties: List[str] = field(default_factory=list)
    is_finesse: bool = False
    is_heavy: bool = False
    is_light: bool = False
    is_loaded: bool = False
    is_two_handed: bool = False
    is_versatile: bool = False
    versatile_damage: str = "d8"
    description: str = ""
    weight: float = 0.0
    value: int = 0
    
    @property
    def item_type(self) -> ItemType:
        return ItemType.WEAPON
    
    def __str__(self) -> str:
        return f"{self.name} (Arme)"
    
    def get_attack_info(self) -> str:
        """Get weapon attack information"""
        info = []
        info.append(f"{self.name} - {self.weapon_type.value}")
        info.append(f"Dégâts: {self.damage_dice} {self.damage_type.value}")
        
        if self.range[1] > 0:
            info.append(f"Portée: {self.range[0]}/{self.range[1]} pieds")
        else:
            info.append("Portée: Mêlée")
        
        if self.properties:
            info.append(f"Propriétés: {', '.join(self.properties)}")
        
        return "\n".join(info)


@dataclass
class Armor:
    """Armor class"""
    name: str
    armor_type: ArmorType = ArmorType.LIGHT
    armor_class: int = 10
    max_dex_bonus: int = 99  # Maximum dexterity bonus that applies
    stealth_disadvantage: bool = False
    strength_requirement: Optional[int] = None
    description: str = ""
    weight: float = 0.0
    value: int = 0
    
    @property
    def item_type(self) -> ItemType:
        return ItemType.ARMOR
    
    def __str__(self) -> str:
        return f"{self.name} (Armure)"
    
    def get_ac_info(self) -> str:
        """Get armor class information"""
        info = []
        info.append(f"{self.name} - {self.armor_type.value}")
        info.append(f"CA: {self.armor_class}")
        info.append(f"Bonus de Dextérité max: {self.max_dex_bonus}")
        
        if self.stealth_disadvantage:
            info.append("Désavantage en Discrétion")
        
        if self.strength_requirement:
            info.append(f"Force requise: {self.strength_requirement}")
        
        return "\n".join(info)


@dataclass
class Potion:
    """Potion class"""
    name: str
    effect: str = ""
    duration: str = "Instantané"
    requires_attunement: bool = False
    description: str = ""
    weight: float = 0.0
    value: int = 0
    
    @property
    def item_type(self) -> ItemType:
        return ItemType.POTION
    
    def __str__(self) -> str:
        return f"{self.name} (Potion)"


# Predefined weapons
WEAPONS = {
    "dague": Weapon(
        name="Dague",
        weapon_type=WeaponType.SIMPLE_MELEE,
        damage_dice="d4",
        damage_type=DamageType.PIERCING,
        range=(5, 20),
        properties=["Finesse", "Légère", "Lancer"],
        is_finesse=True,
        is_light=True,
        weight=1,
        value=2
    ),
    "épée courte": Weapon(
        name="Épée courte",
        weapon_type=WeaponType.SIMPLE_MELEE,
        damage_dice="d6",
        damage_type=DamageType.PIERCING,
        range=(5, 0),
        properties=["Finesse", "Légère"],
        is_finesse=True,
        is_light=True,
        weight=2,
        value=10
    ),
    "épée longue": Weapon(
        name="Épée longue",
        weapon_type=WeaponType.MARTIAL_MELEE,
        damage_dice="d8",
        damage_type=DamageType.SLASHING,
        range=(5, 0),
        properties=["Versatile"],
        is_versatile=True,
        versatile_damage="d10",
        weight=3,
        value=15
    ),
    "hache de guerre": Weapon(
        name="Hache de guerre",
        weapon_type=WeaponType.MARTIAL_MELEE,
        damage_dice="d8",
        damage_type=DamageType.SLASHING,
        range=(5, 0),
        properties=["Versatile"],
        is_versatile=True,
        versatile_damage="d10",
        weight=4,
        value=25
    ),
    "arc court": Weapon(
        name="Arc court",
        weapon_type=WeaponType.SIMPLE_RANGED,
        damage_dice="d6",
        damage_type=DamageType.PIERCING,
        range=(80, 320),
        properties=["Légère", "Rechargement"],
        is_light=True,
        is_loaded=True,
        weight=2,
        value=25
    ),
    "arc long": Weapon(
        name="Arc long",
        weapon_type=WeaponType.MARTIAL_RANGED,
        damage_dice="d8",
        damage_type=DamageType.PIERCING,
        range=(150, 600),
        properties=["Lourd", "Rechargement"],
        is_heavy=True,
        is_loaded=True,
        weight=2,
        value=50
    ),
    "fléchette": Weapon(
        name="Fléchette",
        weapon_type=WeaponType.SIMPLE_RANGED,
        damage_dice="d4",
        damage_type=DamageType.PIERCING,
        range=(20, 60),
        properties=["Finesse", "Lancer"],
        is_finesse=True,
        weight=0.5,
        value=5
    ),
    "massue": Weapon(
        name="Massue",
        weapon_type=WeaponType.SIMPLE_MELEE,
        damage_dice="d6",
        damage_type=DamageType.BLUDGEONING,
        range=(5, 0),
        properties=["Légère"],
        is_light=True,
        weight=4,
        value=5
    ),
    "bâton": Weapon(
        name="Bâton",
        weapon_type=WeaponType.SIMPLE_MELEE,
        damage_dice="d6",
        damage_type=DamageType.BLUDGEONING,
        range=(5, 0),
        properties=["Versatile"],
        is_versatile=True,
        versatile_damage="d8",
        weight=4,
        value=5
    ),
}

# Predefined armor
ARMORS = {
    "armure de cuir": Armor(
        name="Armure de cuir",
        armor_type=ArmorType.LIGHT,
        armor_class=11,
        max_dex_bonus=99,
        stealth_disadvantage=False,
        weight=10,
        value=10
    ),
    "armure de cuir clouté": Armor(
        name="Armure de cuir clouté",
        armor_type=ArmorType.LIGHT,
        armor_class=12,
        max_dex_bonus=99,
        stealth_disadvantage=False,
        weight=13,
        value=45
    ),
    "cotte de mailles": Armor(
        name="Cotte de mailles",
        armor_type=ArmorType.MEDIUM,
        armor_class=14,
        max_dex_bonus=2,
        stealth_disadvantage=True,
        weight=45,
        value=50
    ),
    "armure de plaques": Armor(
        name="Armure de plaques",
        armor_type=ArmorType.HEAVY,
        armor_class=18,
        max_dex_bonus=0,
        stealth_disadvantage=True,
        strength_requirement=15,
        weight=65,
        value=1500
    ),
    "bouclier": Armor(
        name="Bouclier",
        armor_type=ArmorType.SHIELD,
        armor_class=2,  # Bonus to AC
        max_dex_bonus=99,
        stealth_disadvantage=False,
        weight=6,
        value=10
    ),
}

# Predefined potions
POTIONS = {
    "potion de soins": Potion(
        name="Potion de soins",
        description="Restaure 2d4+2 points de vie",
        effect="2d4+2 HP",
        duration="Instantané",
        weight=0.5,
        value=50
    ),
    "potion de soins supérieurs": Potion(
        name="Potion de soins supérieurs",
        description="Restaure 4d4+4 points de vie",
        effect="4d4+4 HP",
        duration="Instantané",
        weight=0.5,
        value=200
    ),
    "potion de force": Potion(
        name="Potion de force",
        description="Bonus de +2 à la Force pendant 1 heure",
        effect="+2 STR",
        duration="1 heure",
        weight=0.5,
        value=100
    ),
    "potion de dextérité": Potion(
        name="Potion de dextérité",
        description="Bonus de +2 à la Dextérité pendant 1 heure",
        effect="+2 DEX",
        duration="1 heure",
        weight=0.5,
        value=100
    ),
}

# Predefined miscellaneous items
MISC_ITEMS = {
    "corde": Item(
        name="Corde (15 mètres)",
        item_type=ItemType.MISC,
        description="Corde solide en chanvre",
        weight=10,
        value=1
    ),
    "torche": Item(
        name="Torche",
        item_type=ItemType.MISC,
        description="Éclaire 20 pieds, dure 1 heure",
        weight=1,
        value=1
    ),
    "lanterne": Item(
        name="Lanterne",
        item_type=ItemType.MISC,
        description="Éclaire 30 pieds",
        weight=2,
        value=5
    ),
    "huile": Item(
        name="Fiole d'huile",
        item_type=ItemType.MISC,
        description="1 pint d'huile, brûle 6 heures",
        weight=1,
        value=1
    ),
    "ration": Item(
        name="Ration (1 jour)",
        item_type=ItemType.FOOD,
        description="Nourriture pour une journée",
        weight=2,
        value=5
    ),
    "sac à composantes": Item(
        name="Sac à composantes",
        item_type=ItemType.TOOL,
        description="Contient des composantes matérielles pour sorts",
        weight=3,
        value=25
    ),
}

# Combine all items
ALL_ITEMS = {**WEAPONS, **ARMORS, **POTIONS, **MISC_ITEMS}


def get_item_by_name(name: str) -> Optional[Item]:
    """Get an item by its name"""
    return ALL_ITEMS.get(name.lower())


def get_random_item(item_type: Optional[ItemType] = None) -> Item:
    """Get a random item"""
    import random
    
    if item_type:
        if item_type == ItemType.WEAPON:
            return random.choice(list(WEAPONS.values()))
        elif item_type == ItemType.ARMOR:
            return random.choice(list(ARMORS.values()))
        elif item_type == ItemType.POTION:
            return random.choice(list(POTIONS.values()))
        else:
            return random.choice(list(MISC_ITEMS.values()))
    else:
        all_items_list = list(ALL_ITEMS.values())
        return random.choice(all_items_list)
