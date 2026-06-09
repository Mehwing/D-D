"""
Character system for D&D
"""
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .dice import Dice, DiceResult


class Race(Enum):
    """Character races"""
    HUMAN = "Humain"
    ELF = "Elfe"
    DWARF = "Nain"
    HALFLING = "Halfelin"
    ORC = "Orc"
    TIEFLING = "Tieffelin"
    DRAGONBORN = "Dracónide"
    GNOME = "Gnome"
    HALF_ELF = "Demi-Elfe"
    HALF_ORC = "Demi-Orc"


class Class(Enum):
    """Character classes"""
    FIGHTER = "Guerrier"
    WIZARD = "Magicien"
    ROGUE = "Voleur"
    CLERIC = "Clerc"
    BARBARIAN = "Barbare"
    PALADIN = "Paladin"
    RANGER = "Rôdeur"
    MONK = "Moine"
    BARD = "Barde"
    DRUID = "Druide"
    SORCERER = "Ensorceleur"
    WARLOCK = "Occultiste"


class Alignment(Enum):
    """Character alignments"""
    LAWFUL_GOOD = "Loyal Bon"
    NEUTRAL_GOOD = "Neutre Bon"
    CHAOTIC_GOOD = "Chaotique Bon"
    LAWFUL_NEUTRAL = "Loyal Neutre"
    TRUE_NEUTRAL = "Neutre"
    CHAOTIC_NEUTRAL = "Chaotique Neutre"
    LAWFUL_EVIL = "Loyal Mauvais"
    NEUTRAL_EVIL = "Neutre Mauvais"
    CHAOTIC_EVIL = "Chaotique Mauvais"


# Race modifiers
RACE_MODIFIERS = {
    Race.HUMAN: {'str': 1, 'dex': 1, 'con': 1, 'int': 1, 'wis': 1, 'cha': 1},
    Race.ELF: {'dex': 2, 'int': 1},
    Race.DWARF: {'con': 2, 'wis': 1},
    Race.HALFLING: {'dex': 2, 'cha': 1},
    Race.ORC: {'str': 2, 'con': 1},
    Race.TIEFLING: {'int': 1, 'cha': 2},
    Race.DRAGONBORN: {'str': 2, 'cha': 1},
    Race.GNOME: {'int': 2, 'con': 1},
    Race.HALF_ELF: {'cha': 2, 'dex': 1, 'con': 1},
    Race.HALF_ORC: {'str': 2, 'con': 1},
}

# Class hit dice
CLASS_HIT_DICE = {
    Class.FIGHTER: 'd10',
    Class.WIZARD: 'd6',
    Class.ROGUE: 'd8',
    Class.CLERIC: 'd8',
    Class.BARBARIAN: 'd12',
    Class.PALADIN: 'd10',
    Class.RANGER: 'd10',
    Class.MONK: 'd8',
    Class.BARD: 'd8',
    Class.DRUID: 'd8',
    Class.SORCERER: 'd6',
    Class.WARLOCK: 'd8',
}


@dataclass
class Stats:
    """Character statistics"""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2
    
    @property
    def constitution_modifier(self) -> int:
        return (self.constitution - 10) // 2
    
    @property
    def intelligence_modifier(self) -> int:
        return (self.intelligence - 10) // 2
    
    @property
    def wisdom_modifier(self) -> int:
        return (self.wisdom - 10) // 2
    
    @property
    def charisma_modifier(self) -> int:
        return (self.charisma - 10) // 2
    
    def get_modifier(self, stat_name: str) -> int:
        """Get modifier for a stat by name"""
        stat_map = {
            'str': self.strength_modifier,
            'dex': self.dexterity_modifier,
            'con': self.constitution_modifier,
            'int': self.intelligence_modifier,
            'wis': self.wisdom_modifier,
            'cha': self.charisma_modifier
        }
        return stat_map.get(stat_name, 0)
    
    def to_dict(self) -> Dict:
        """Convert stats to dictionary"""
        return {
            'strength': self.strength,
            'dexterity': self.dexterity,
            'constitution': self.constitution,
            'intelligence': self.intelligence,
            'wisdom': self.wisdom,
            'charisma': self.charisma
        }


@dataclass
class Character:
    """D&D Character class"""
    name: str
    race: Race
    char_class: Class
    level: int = 1
    background: str = ""
    alignment: Alignment = Alignment.TRUE_NEUTRAL
    experience: int = 0
    stats: Stats = field(default_factory=Stats)
    max_hp: int = 10
    current_hp: int = 10
    armor_class: int = 10
    initiative: int = 0
    speed: int = 30
    proficiency_bonus: int = 2
    
    # Skills and abilities
    skills: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    
    # Inventory
    inventory: List['Item'] = field(default_factory=list)
    gold: int = 0
    
    # Spellcasting
    spell_slots: Dict[int, int] = field(default_factory=dict)
    known_spells: List[str] = field(default_factory=list)
    
    # Combat
    weapons: List['Weapon'] = field(default_factory=list)
    armor: Optional['Armor'] = None
    shield: bool = False
    
    def __post_init__(self):
        """Initialize character with proper values"""
        if not hasattr(self, 'stats') or self.stats is None:
            self.stats = Stats()
        
        # Apply race modifiers
        self._apply_race_modifiers()
        
        # Calculate initial HP
        if self.max_hp == 10:  # Default value
            hit_dice = CLASS_HIT_DICE.get(self.char_class, 'd8')
            con_mod = self.stats.constitution_modifier
            self.max_hp = Dice.roll(hit_dice, 1, con_mod).value
            self.current_hp = self.max_hp
        
        # Calculate armor class
        self._calculate_armor_class()
        
        # Calculate initiative
        self.initiative = self.stats.dexterity_modifier
        
        # Set spell slots based on class and level
        self._initialize_spell_slots()
    
    def _apply_race_modifiers(self):
        """Apply racial modifiers to stats"""
        modifiers = RACE_MODIFIERS.get(self.race, {})
        for stat, mod in modifiers.items():
            if stat == 'str':
                self.stats.strength += mod
            elif stat == 'dex':
                self.stats.dexterity += mod
            elif stat == 'con':
                self.stats.constitution += mod
            elif stat == 'int':
                self.stats.intelligence += mod
            elif stat == 'wis':
                self.stats.wisdom += mod
            elif stat == 'cha':
                self.stats.charisma += mod
    
    def _calculate_armor_class(self):
        """Calculate armor class based on equipment"""
        base_ac = 10 + self.stats.dexterity_modifier
        
        if self.armor:
            # Armor provides base AC, dexterity modifier may be limited
            base_ac = self.armor.armor_class
            # For most armor, dexterity modifier is limited or not added
            if self.armor.armor_type in ['light', 'medium']:
                base_ac += min(self.stats.dexterity_modifier, self.armor.max_dex_bonus)
        
        if self.shield:
            base_ac += 2
        
        self.armor_class = base_ac
    
    def _initialize_spell_slots(self):
        """Initialize spell slots based on class and level"""
        # Full casters (wizard, cleric, druid, sorcerer, bard)
        full_casters = [Class.WIZARD, Class.CLERIC, Class.DRUID, Class.SORCERER, Class.BARD]
        # Half casters (paladin, ranger)
        half_casters = [Class.PALADIN, Class.RANGER]
        # Third casters (warlock)
        third_casters = [Class.WARLOCK]
        
        if self.char_class in full_casters:
            # Full casters get spell slots at every level
            spell_slot_table = {
                1: {1: 2},
                2: {1: 3},
                3: {1: 4, 2: 2},
                4: {1: 4, 2: 3},
                5: {1: 4, 2: 3, 3: 2},
                6: {1: 4, 2: 3, 3: 3},
                7: {1: 4, 2: 3, 3: 3, 4: 1},
                8: {1: 4, 2: 3, 3: 3, 4: 2},
                9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
                10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            }
            if self.level in spell_slot_table:
                self.spell_slots = spell_slot_table[self.level]
            else:
                # Higher levels
                self.spell_slots = {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1}
        
        elif self.char_class in half_casters:
            # Half casters get spells at half level (rounded up)
            effective_level = (self.level + 1) // 2
            spell_slot_table = {
                1: {1: 2},
                2: {1: 3},
                3: {1: 4, 2: 2},
                4: {1: 4, 2: 3},
                5: {1: 4, 2: 3, 3: 2},
            }
            if effective_level in spell_slot_table:
                self.spell_slots = spell_slot_table[effective_level]
            else:
                self.spell_slots = {1: 4, 2: 3, 3: 3}
        
        elif self.char_class in third_casters:
            # Warlock has pact magic
            if self.level >= 1:
                self.spell_slots = {1: 1}
            if self.level >= 2:
                self.spell_slots[1] = 2
            if self.level >= 3:
                self.spell_slots = {1: 2, 2: 1}
            if self.level >= 5:
                self.spell_slots = {1: 2, 2: 1, 3: 1}
    
    def roll_initiative(self) -> DiceResult:
        """Roll initiative"""
        return Dice.roll('d20', 1, self.stats.dexterity_modifier)
    
    def roll_attack(self, weapon_bonus: int = 0) -> DiceResult:
        """Roll attack roll"""
        # Base attack bonus depends on class and level
        bab = self.proficiency_bonus
        if self.char_class in [Class.FIGHTER, Class.BARBARIAN, Class.PALADIN, Class.RANGER]:
            bab += self.level // 4  # Simplified
        
        # Add weapon bonus and strength/dexterity modifier
        if weapon_bonus == 0:
            # Use strength for melee, dexterity for ranged
            weapon_bonus = self.stats.strength_modifier
        
        return Dice.roll('d20', 1, bab + weapon_bonus)
    
    def roll_damage(self, damage_dice: str, modifier: Optional[int] = None) -> DiceResult:
        """Roll damage"""
        if modifier is None:
            modifier = self.stats.strength_modifier
        return Dice.roll(damage_dice, 1, modifier)
    
    def roll_skill_check(self, skill: str, advantage: bool = False, disadvantage: bool = False) -> Tuple[DiceResult, Optional[Tuple[DiceResult, DiceResult]]]:
        """Roll a skill check"""
        # Get the relevant stat modifier
        skill_stats = {
            'athletics': 'str',
            'acrobatics': 'dex',
            'sleight_of_hand': 'dex',
            'stealth': 'dex',
            'arcana': 'int',
            'history': 'int',
            'investigation': 'int',
            'nature': 'int',
            'religion': 'int',
            'animal_handling': 'wis',
            'insight': 'wis',
            'medicine': 'wis',
            'perception': 'wis',
            'survival': 'wis',
            'deception': 'cha',
            'intimidation': 'cha',
            'performance': 'cha',
            'persuasion': 'cha'
        }
        
        stat = skill_stats.get(skill.lower(), 'dex')
        modifier = self.stats.get_modifier(stat)
        
        # Add proficiency bonus if character has the skill
        if skill.lower() in [s.lower() for s in self.skills]:
            modifier += self.proficiency_bonus
        
        if advantage:
            result, roll1, roll2 = roll_advantage('d20', modifier)
            return result, (roll1, roll2)
        elif disadvantage:
            result, roll1, roll2 = roll_disadvantage('d20', modifier)
            return result, (roll1, roll2)
        else:
            return Dice.roll('d20', 1, modifier), None
    
    def take_damage(self, amount: int) -> int:
        """Take damage"""
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0
        return self.current_hp
    
    def heal(self, amount: int) -> int:
        """Heal"""
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        return self.current_hp
    
    def level_up(self):
        """Level up the character"""
        self.level += 1
        self.proficiency_bonus = 2 + (self.level - 1) // 4
        
        # Increase HP
        hit_dice = CLASS_HIT_DICE.get(self.char_class, 'd8')
        con_mod = self.stats.constitution_modifier
        hp_increase = Dice.roll(hit_dice, 1, con_mod).value
        self.max_hp += hp_increase
        self.current_hp = self.max_hp
        
        # Update spell slots
        self._initialize_spell_slots()
        
        # Add new features based on class
        self._add_class_features()
    
    def _add_class_features(self):
        """Add class features on level up"""
        class_features = {
            Class.FIGHTER: {
                2: "Action Surge",
                3: "Martial Archetype",
                5: "Extra Attack",
                6: "Ability Score Improvement",
            },
            Class.WIZARD: {
                2: "Arcane Tradition",
                3: "Ritual Casting",
                5: "Arcane Recovery",
            },
            Class.ROGUE: {
                2: "Cunning Action",
                3: "Roguish Archetype",
                5: "Uncanny Dodge",
            },
            Class.CLERIC: {
                2: "Divine Domain",
                3: "Channel Divinity",
            },
            Class.BARBARIAN: {
                2: "Rage Damage",
                3: "Primal Path",
                5: "Extra Attack",
            },
            Class.PALADIN: {
                2: "Divine Smite",
                3: "Sacred Oath",
            },
            Class.RANGER: {
                2: "Fighting Style",
                3: "Ranger Archetype",
            },
        }
        
        if self.char_class in class_features:
            features = class_features[self.char_class]
            if self.level in features:
                self.features.append(features[self.level])
    
    def add_to_inventory(self, item: 'Item'):
        """Add item to inventory"""
        self.inventory.append(item)
    
    def remove_from_inventory(self, item: 'Item') -> bool:
        """Remove item from inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def equip_weapon(self, weapon: 'Weapon'):
        """Equip a weapon"""
        if weapon not in self.weapons:
            self.weapons.append(weapon)
    
    def equip_armor(self, armor: 'Armor'):
        """Equip armor"""
        self.armor = armor
        self._calculate_armor_class()
    
    def equip_shield(self, equip: bool = True):
        """Equip or unequip shield"""
        self.shield = equip
        self._calculate_armor_class()
    
    def to_dict(self) -> Dict:
        """Convert character to dictionary for display"""
        return {
            'name': self.name,
            'race': self.race.value,
            'class': self.char_class.value,
            'level': self.level,
            'alignment': self.alignment.value,
            'background': self.background,
            'experience': self.experience,
            'stats': self.stats.to_dict(),
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'armor_class': self.armor_class,
            'initiative': self.initiative,
            'speed': self.speed,
            'proficiency_bonus': self.proficiency_bonus,
            'skills': self.skills,
            'features': self.features,
            'inventory': [item.name for item in self.inventory],
            'gold': self.gold,
            'spell_slots': self.spell_slots,
            'known_spells': self.known_spells,
            'weapons': [w.name for w in self.weapons],
            'armor': self.armor.name if self.armor else None,
            'shield': self.shield
        }
    
    def get_summary(self) -> str:
        """Get a summary of the character"""
        summary = []
        summary.append(f"{self.name} - {self.race.value} {self.char_class.value} (Niveau {self.level})")
        summary.append(f"Alignement: {self.alignment.value}")
        summary.append(f"PV: {self.current_hp}/{self.max_hp}")
        summary.append(f"CA: {self.armor_class}")
        summary.append(f"Initiative: +{self.initiative}")
        summary.append("")
        summary.append("Caractéristiques:")
        summary.append(f"  FOR: {self.stats.strength} ({self.stats.strength_modifier:+d})")
        summary.append(f"  DEX: {self.stats.dexterity} ({self.stats.dexterity_modifier:+d})")
        summary.append(f"  CON: {self.stats.constitution} ({self.stats.constitution_modifier:+d})")
        summary.append(f"  INT: {self.stats.intelligence} ({self.stats.intelligence_modifier:+d})")
        summary.append(f"  SAG: {self.stats.wisdom} ({self.stats.wisdom_modifier:+d})")
        summary.append(f"  CHA: {self.stats.charisma} ({self.stats.charisma_modifier:+d})")
        
        return "\n".join(summary)


def create_random_character(name: str = "", level: int = 1) -> Character:
    """Create a random character"""
    if not name:
        first_names = ["Alaric", "Baldric", "Cedric", "Darian", "Eldrin", "Faelar", "Garrick", 
                      "Haldor", "Isolde", "Jareth", "Kael", "Lysara", "Mirabel", "Nyssa", 
                      "Orion", "Peregrine", "Quill", "Ravena", "Sylvia", "Thalion"]
        last_names = ["Stormborn", "Ironfoot", "Whisperwind", "Darkheart", "Brightblade", 
                     "Shadowfang", "Moonshadow", "Stonebraid", "Wildheart", "Frostveil"]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    race = random.choice(list(Race))
    char_class = random.choice(list(Class))
    alignment = random.choice(list(Alignment))
    
    # Generate stats using standard array (15, 14, 13, 12, 10, 8)
    standard_array = [15, 14, 13, 12, 10, 8]
    random.shuffle(standard_array)
    
    stats = Stats(
        strength=standard_array[0],
        dexterity=standard_array[1],
        constitution=standard_array[2],
        intelligence=standard_array[3],
        wisdom=standard_array[4],
        charisma=standard_array[5]
    )
    
    # Create character
    character = Character(
        name=name,
        race=race,
        char_class=char_class,
        level=level,
        alignment=alignment,
        stats=stats
    )
    
    # Add some random skills
    all_skills = [
        "Athletics", "Acrobatics", "Sleight of Hand", "Stealth",
        "Arcana", "History", "Investigation", "Nature", "Religion",
        "Animal Handling", "Insight", "Medicine", "Perception", "Survival",
        "Deception", "Intimidation", "Performance", "Persuasion"
    ]
    character.skills = random.sample(all_skills, k=4)
    
    # Add some starting gold
    character.gold = random.randint(50, 200)
    
    return character


# Import Item, Weapon, Armor for type hints
from .item import Item, Weapon, Armor, ItemType
