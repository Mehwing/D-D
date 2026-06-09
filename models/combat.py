"""
Combat system for D&D
"""
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .dice import Dice, DiceResult
from .character import Character
from .item import Weapon, Armor, DamageType


class EnemyType(Enum):
    """Types of enemies"""
    HUMANOID = "Humanoïde"
    BEAST = "Bête"
    MONSTROSITY = "Monstrosité"
    UNDEAD = "Mort-vivant"
    DRAGON = "Dragon"
    FIEND = "Démon"
    ELEMENTAL = "Élémentaire"
    CONSTRUCT = "Construction"
    ABERRATION = "Aberration"


class EnemySize(Enum):
    """Sizes of enemies"""
    TINY = "Minuscule"
    SMALL = "Petit"
    MEDIUM = "Moyen"
    LARGE = "Grand"
    HUGE = "Énorme"
    GARGANTUAN = "Colossal"


@dataclass
class Enemy:
    """Enemy class for combat"""
    name: str
    enemy_type: EnemyType
    size: EnemySize = EnemySize.MEDIUM
    armor_class: int = 10
    hit_points: int = 10
    current_hp: int = 10
    speed: int = 30
    
    # Stats
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # Combat
    challenge_rating: float = 0.125
    proficiency_bonus: int = 2
    
    # Actions
    actions: List[str] = field(default_factory=list)
    multiattack: bool = False
    
    # Damage resistances/immunities
    damage_resistances: List[str] = field(default_factory=list)
    damage_immunities: List[str] = field(default_factory=list)
    condition_immunities: List[str] = field(default_factory=list)
    
    # Senses
    senses: List[str] = field(default_factory=list)
    passive_perception: int = 10
    
    # Languages
    languages: str = "—"
    
    def __post_init__(self):
        """Initialize enemy"""
        if not hasattr(self, 'current_hp') or self.current_hp == 10:
            self.current_hp = self.hit_points
    
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
    def initiative(self) -> int:
        return self.dexterity_modifier
    
    def roll_initiative(self) -> DiceResult:
        """Roll initiative"""
        return Dice.roll('d20', 1, self.dexterity_modifier)
    
    def roll_attack(self, attack_bonus: int = 0) -> DiceResult:
        """Roll attack roll"""
        # Default attack bonus based on CR
        if attack_bonus == 0:
            attack_bonus = self.proficiency_bonus + self.strength_modifier
        return Dice.roll('d20', 1, attack_bonus)
    
    def roll_damage(self, damage_dice: str, modifier: int = 0) -> DiceResult:
        """Roll damage"""
        if modifier == 0:
            modifier = self.strength_modifier
        return Dice.roll(damage_dice, 1, modifier)
    
    def take_damage(self, amount: int, damage_type: str = "slashing") -> Tuple[int, str]:
        """Take damage, return (remaining_hp, damage_result)"""
        # Check for resistances
        if damage_type.lower() in [dt.lower() for dt in self.damage_resistances]:
            amount = amount // 2
            result = f"{self.name} résiste aux dégâts {damage_type}! Dégâts réduits à {amount}."
        elif damage_type.lower() in [dt.lower() for dt in self.damage_immunities]:
            amount = 0
            result = f"{self.name} est immunisé contre les dégâts {damage_type}! Aucun dégât."
        else:
            result = f"{self.name} subit {amount} dégâts {damage_type}."
        
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0
        
        return self.current_hp, result
    
    def heal(self, amount: int) -> int:
        """Heal"""
        self.current_hp += amount
        if self.current_hp > self.hit_points:
            self.current_hp = self.hit_points
        return self.current_hp
    
    def is_defeated(self) -> bool:
        """Check if enemy is defeated"""
        return self.current_hp <= 0
    
    def get_summary(self) -> str:
        """Get enemy summary"""
        summary = []
        summary.append(f"{self.name} ({self.size.value} {self.enemy_type.value})")
        summary.append(f"CA: {self.armor_class}, PV: {self.current_hp}/{self.hit_points}")
        summary.append(f"Vitesse: {self.speed} pieds")
        summary.append(f"FOR: {self.strength} ({self.strength_modifier:+d}), DEX: {self.dexterity} ({self.dexterity_modifier:+d}), CON: {self.constitution} ({self.constitution_modifier:+d})")
        summary.append(f"INT: {self.intelligence}, SAG: {self.wisdom}, CHA: {self.charisma}")
        summary.append(f"DD: {self.challenge_rating}")
        
        if self.damage_resistances:
            summary.append(f"Résistances: {', '.join(self.damage_resistances)}")
        if self.damage_immunities:
            summary.append(f"Immunités: {', '.join(self.damage_immunities)}")
        if self.condition_immunities:
            summary.append(f"Immunités aux conditions: {', '.join(self.condition_immunities)}")
        
        if self.actions:
            summary.append("Actions:")
            for action in self.actions:
                summary.append(f"  - {action}")
        
        return "\n".join(summary)


@dataclass
class Combat:
    """Combat encounter class"""
    name: str
    enemies: List[Enemy] = field(default_factory=list)
    description: str = ""
    difficulty: str = "Facile"
    experience_reward: int = 0
    
    # Combat state
    current_round: int = 0
    current_turn: int = 0
    combatants: List[Tuple[Character, int]] = field(default_factory=list)  # (character, initiative)
    enemies_in_combat: List[Tuple[Enemy, int]] = field(default_factory=list)  # (enemy, initiative)
    turn_order: List[Tuple[str, int, bool]] = field(default_factory=list)  # (name, initiative, is_player)
    
    def add_enemy(self, enemy: Enemy):
        """Add an enemy to the combat"""
        self.enemies.append(enemy)
    
    def add_player(self, character: Character):
        """Add a player character to the combat"""
        self.combatants.append((character, 0))
    
    def start_combat(self, player_characters: List[Character]):
        """Start combat with initiative rolls"""
        self.current_round = 0
        self.current_turn = 0
        self.combatants = []
        self.enemies_in_combat = []
        self.turn_order = []
        
        # Add player characters
        for character in player_characters:
            initiative = character.roll_initiative().value
            self.combatants.append((character, initiative))
            self.turn_order.append((character.name, initiative, True))
        
        # Add enemies
        for enemy in self.enemies:
            initiative = enemy.roll_initiative().value
            self.enemies_in_combat.append((enemy, initiative))
            self.turn_order.append((enemy.name, initiative, False))
        
        # Sort by initiative (descending)
        self.turn_order.sort(key=lambda x: x[1], reverse=True)
        
        return self.turn_order
    
    def next_turn(self) -> Optional[Tuple[str, bool]]:
        """Move to next turn, return (name, is_player) or None if combat ended"""
        if self.current_turn >= len(self.turn_order) - 1:
            self.current_round += 1
            self.current_turn = 0
            
            # Check if combat should end
            if self._check_combat_end():
                return None
        else:
            self.current_turn += 1
        
        if self.current_turn < len(self.turn_order):
            return self.turn_order[self.current_turn][0], self.turn_order[self.current_turn][2]
        return None
    
    def _check_combat_end(self) -> bool:
        """Check if combat should end"""
        # Check if all enemies are defeated
        all_enemies_defeated = all(enemy.is_defeated() for enemy, _ in self.enemies_in_combat)
        
        # Check if all players are defeated
        all_players_defeated = all(char.current_hp <= 0 for char, _ in self.combatants)
        
        return all_enemies_defeated or all_players_defeated
    
    def get_current_combatant(self) -> Optional[Tuple[str, bool]]:
        """Get current combatant"""
        if self.current_turn < len(self.turn_order):
            return self.turn_order[self.current_turn][0], self.turn_order[self.current_turn][2]
        return None
    
    def get_combatant_by_name(self, name: str) -> Optional[Tuple[Character, bool]]:
        """Get combatant by name, return (character or enemy, is_player)"""
        # Check players
        for character, _ in self.combatants:
            if character.name == name:
                return character, True
        
        # Check enemies
        for enemy, _ in self.enemies_in_combat:
            if enemy.name == name:
                return enemy, False
        
        return None
    
    def attack(self, attacker_name: str, target_name: str, weapon: Optional[Weapon] = None) -> str:
        """Perform an attack"""
        attacker, is_player = self.get_combatant_by_name(attacker_name)
        target, is_target_player = self.get_combatant_by_name(target_name)
        
        if not attacker or not target:
            return "Attaquant ou cible introuvable"
        
        if is_player:
            attacker_char: Character = attacker
            attack_roll = attacker_char.roll_attack()
            attack_bonus = attack_roll.value - Dice.roll('d20').value  # Extract modifier
            
            # Get target AC
            if is_target_player:
                target_char: Character = target
                target_ac = target_char.armor_class
            else:
                target_enemy: Enemy = target
                target_ac = target_enemy.armor_class
            
            # Check if hit
            if attack_roll.value >= target_ac:
                # Hit - roll damage
                if weapon:
                    damage_roll = attacker_char.roll_damage(weapon.damage_dice)
                    damage = damage_roll.value
                else:
                    # Unarmed strike
                    damage_roll = Dice.roll('d4', 1, attacker_char.stats.strength_modifier)
                    damage = damage_roll.value
                
                # Apply damage to target
                if is_target_player:
                    target_char: Character = target
                    target_char.take_damage(damage)
                    return f"{attacker_char.name} touche {target_char.name} avec un {attack_roll.value} (CA {target_ac}) et inflige {damage} dégâts! {target_char.name} a maintenant {target_char.current_hp} PV."
                else:
                    target_enemy: Enemy = target
                    _, result = target_enemy.take_damage(damage)
                    return f"{attacker_char.name} touche {target_enemy.name} avec un {attack_roll.value} (CA {target_ac}) et inflige {damage} dégâts! {result}"
            else:
                return f"{attacker_char.name} rate {target_name} avec un {attack_roll.value} (CA {target_ac})."
        else:
            # Enemy attack
            attacker_enemy: Enemy = attacker
            attack_roll = attacker_enemy.roll_attack()
            
            # Get target AC
            if is_target_player:
                target_char: Character = target
                target_ac = target_char.armor_class
            else:
                target_enemy: Enemy = target
                target_ac = target_enemy.armor_class
            
            # Check if hit
            if attack_roll.value >= target_ac:
                # Hit - roll damage (simplified)
                damage_roll = Dice.roll('d6', 1, attacker_enemy.strength_modifier)
                damage = damage_roll.value
                
                # Apply damage to target
                if is_target_player:
                    target_char: Character = target
                    target_char.take_damage(damage)
                    return f"{attacker_enemy.name} touche {target_char.name} avec un {attack_roll.value} (CA {target_ac}) et inflige {damage} dégâts! {target_char.name} a maintenant {target_char.current_hp} PV."
                else:
                    target_enemy: Enemy = target
                    _, result = target_enemy.take_damage(damage)
                    return f"{attacker_enemy.name} touche {target_enemy.name} avec un {attack_roll.value} (CA {target_ac}) et inflige {damage} dégâts! {result}"
            else:
                return f"{attacker_enemy.name} rate {target_name} avec un {attack_roll.value} (CA {target_ac})."
    
    def cast_spell(self, caster_name: str, spell_name: str, target_name: Optional[str] = None) -> str:
        """Cast a spell in combat"""
        from .spell import get_spell_by_name
        
        caster, is_player = self.get_combatant_by_name(caster_name)
        spell = get_spell_by_name(spell_name)
        
        if not caster or not spell:
            return "Lanceur ou sort introuvable"
        
        if is_player:
            caster_char: Character = caster
            
            # Check if caster knows the spell
            if spell_name not in caster_char.known_spells:
                return f"{caster_char.name} ne connaît pas ce sort"
            
            # Check spell slots
            if spell.level > 0:
                if spell.level not in caster_char.spell_slots or caster_char.spell_slots[spell.level] <= 0:
                    return f"{caster_char.name} n'a plus d'emplacements de sort de niveau {spell.level}"
                
                # Use spell slot
                caster_char.spell_slots[spell.level] -= 1
            
            # Cast the spell
            if target_name:
                target, _ = self.get_combatant_by_name(target_name)
                if target:
                    return f"{caster_char.name} lance {spell.name} sur {target_name}! {spell.effect}"
            
            return f"{caster_char.name} lance {spell.name}! {spell.effect}"
        
        return f"{caster_name} lance {spell_name}!"
    
    def get_combat_summary(self) -> str:
        """Get current combat summary"""
        summary = []
        summary.append(f"Combat: {self.name} (Round {self.current_round})")
        summary.append(f"Difficulté: {self.difficulté}")
        summary.append("")
        
        # Players
        summary.append("Joueurs:")
        for character, initiative in self.combatants:
            status = "OK" if character.current_hp > 0 else "INCONSCIENT"
            summary.append(f"  {character.name}: {character.current_hp}/{character.max_hp} PV [{status}] (Initiative: {initiative})")
        
        summary.append("")
        
        # Enemies
        summary.append("Ennemis:")
        for enemy, initiative in self.enemies_in_combat:
            status = "OK" if enemy.current_hp > 0 else "VAINCU"
            summary.append(f"  {enemy.name}: {enemy.current_hp}/{enemy.hit_points} PV [{status}] (Initiative: {initiative})")
        
        summary.append("")
        
        # Turn order
        summary.append("Ordre des tours:")
        for name, initiative, is_player in self.turn_order:
            marker = "→ " if self.current_turn == self.turn_order.index((name, initiative, is_player)) else "  "
            side = "Joueur" if is_player else "Ennemi"
            summary.append(f"{marker}{name} ({side}, Initiative: {initiative})")
        
        return "\n".join(summary)


# Predefined enemies
ENEMIES = {
    "gobelin": Enemy(
        name="Gobelin",
        enemy_type=EnemyType.HUMANOID,
        size=EnemySize.SMALL,
        armor_class=15,
        hit_points=7,
        speed=30,
        strength=8,
        dexterity=14,
        constitution=10,
        intelligence=10,
        wisdom=8,
        charisma=8,
        challenge_rating=0.25,
        proficiency_bonus=2,
        actions=[
            "Attaque de cimeterre. Attaque de mêlée: +4, portée 5 pieds, une cible. Touché: 5 (1d6+2) dégâts tranchants.",
            "Arc court. Attaque à distance: +4, portée 80/320 pieds, une cible. Touché: 5 (1d6+2) dégâts perforants."
        ],
        senses=["vision dans le noir 18 m"],
        passive_perception=9,
        languages="Commun, Gobelin"
    ),
    "orc": Enemy(
        name="Orc",
        enemy_type=EnemyType.HUMANOID,
        size=EnemySize.MEDIUM,
        armor_class=13,
        hit_points=15,
        speed=30,
        strength=16,
        dexterity=12,
        constitution=16,
        intelligence=7,
        wisdom=11,
        charisma=10,
        challenge_rating=0.5,
        proficiency_bonus=2,
        actions=[
            "Hache de guerre. Attaque de mêlée: +5, portée 5 pieds, une cible. Touché: 8 (1d8+3) dégâts tranchants.",
            "Javelot. Attaque de mêlée ou à distance: +5, portée 5 pieds ou 30/120 pieds, une cible. Touché: 6 (1d6+3) dégâts perforants."
        ],
        senses=["vision dans le noir 18 m"],
        passive_perception=10,
        languages="Commun, Orc"
    ),
    "loup": Enemy(
        name="Loup",
        enemy_type=EnemyType.BEAST,
        size=EnemySize.MEDIUM,
        armor_class=13,
        hit_points=11,
        speed=40,
        strength=12,
        dexterity=15,
        constitution=12,
        intelligence=3,
        wisdom=12,
        charisma=6,
        challenge_rating=0.25,
        proficiency_bonus=2,
        actions=[
            "Morsure. Attaque de mêlée: +4, portée 5 pieds, une cible. Touché: 7 (2d4+2) dégâts perforants. Si la cible est une créature, elle doit réussir un jet de sauvegarde de Force DD 11 ou être jetée à terre."
        ],
        senses=["vision dans le noir 18 m, perception passive 13"],
        passive_perception=13,
        languages="—"
    ),
    "squelette": Enemy(
        name="Squelette",
        enemy_type=EnemyType.UNDEAD,
        size=EnemySize.MEDIUM,
        armor_class=15,
        hit_points=13,
        speed=30,
        strength=10,
        dexterity=14,
        constitution=15,
        intelligence=6,
        wisdom=8,
        charisma=5,
        challenge_rating=0.25,
        proficiency_bonus=2,
        actions=[
            "Épée courte. Attaque de mêlée: +4, portée 5 pieds, une cible. Touché: 5 (1d6+2) dégâts perforants.",
            "Arc court. Attaque à distance: +4, portée 80/320 pieds, une cible. Touché: 5 (1d6+2) dégâts perforants."
        ],
        damage_immunities=["poison"],
        condition_immunities=["empoisonné", "épuisé"],
        senses=["vision dans le noir 18 m"],
        passive_perception=9,
        languages="comprend les langues qu'il connaissait de son vivant"
    ),
    "zombie": Enemy(
        name="Zombie",
        enemy_type=EnemyType.UNDEAD,
        size=EnemySize.MEDIUM,
        armor_class=8,
        hit_points=22,
        speed=20,
        strength=13,
        dexterity=6,
        constitution=16,
        intelligence=3,
        wisdom=6,
        charisma=5,
        challenge_rating=0.25,
        proficiency_bonus=2,
        actions=[
            "Coup. Attaque de mêlée: +3, portée 5 pieds, une cible. Touché: 6 (1d8+2) dégâts contondants."
        ],
        damage_immunities=["poison"],
        condition_immunities=["empoisonné", "épuisé"],
        senses=["vision dans le noir 18 m"],
        passive_perception=8,
        languages="comprend les langues qu'il connaissait de son vivant"
    ),
    "troll": Enemy(
        name="Troll",
        enemy_type=EnemyType.MONSTROSITY,
        size=EnemySize.LARGE,
        armor_class=15,
        hit_points=84,
        speed=30,
        strength=18,
        dexterity=13,
        constitution=16,
        intelligence=7,
        wisdom=9,
        charisma=7,
        challenge_rating=5,
        proficiency_bonus=3,
        multiattack=True,
        actions=[
            "Attaques multiples. Le troll effectue trois attaques: une avec sa morsure et deux avec ses griffes.",
            "Morsure. Attaque de mêlée: +7, portée 5 pieds, une cible. Touché: 7 (1d6+4) dégâts perforants.",
            "Griffe. Attaque de mêlée: +7, portée 5 pieds, une cible. Touché: 11 (2d6+4) dégâts tranchants."
        ],
        damage_resistances=["contondant", "perforant", "tranchant"],
        senses=["vision dans le noir 18 m"],
        passive_perception=12,
        languages="Giant"
    ),
    "dragon vert jeune": Enemy(
        name="Dragon vert jeune",
        enemy_type=EnemyType.DRAGON,
        size=EnemySize.LARGE,
        armor_class=18,
        hit_points=133,
        speed=40,
        strength=19,
        dexterity=12,
        constitution=17,
        intelligence=16,
        wisdom=13,
        charisma=15,
        challenge_rating=8,
        proficiency_bonus=4,
        multiattack=True,
        actions=[
            "Attaques multiples. Le dragon effectue trois attaques: une avec sa morsure et deux avec ses griffes.",
            "Morsure. Attaque de mêlée: +7, portée 10 pieds, une cible. Touché: 15 (2d10+4) dégâts perforants + 7 (2d6) dégâts de poison.",
            "Griffe. Attaque de mêlée: +7, portée 5 pieds, une cible. Touché: 11 (2d6+4) dégâts tranchants.",
            "Souffle de poison (Recharge 5-6). Le dragon crache du gaz toxique dans un cône de 15 mètres. Chaque créature dans la zone doit réussir un jet de sauvegarde de Constitution DD 15 ou subir 42 (12d6) dégâts de poison."
        ],
        damage_immunities=["poison"],
        condition_immunities=["empoisonné"],
        senses=["vision dans le noir 18 m, vision aveugle 18 m, perception passive 16"],
        passive_perception=16,
        languages="Commun, Draconique"
    ),
}


def get_enemy_by_name(name: str) -> Optional[Enemy]:
    """Get an enemy by its name"""
    return ENEMIES.get(name.lower())


def get_random_enemy(cr_min: float = 0, cr_max: float = 10) -> Enemy:
    """Get a random enemy within CR range"""
    import random
    
    valid_enemies = [e for e in ENEMIES.values() if cr_min <= e.challenge_rating <= cr_max]
    if valid_enemies:
        return random.choice(valid_enemies)
    return random.choice(list(ENEMIES.values()))


# Predefined combat encounters
COMBAT_ENCOUNTERS = {
    "embuscade de gobelins": Combat(
        name="Embuscade de gobelins",
        enemies=[
            ENEMIES["gobelin"],
            ENEMIES["gobelin"],
            ENEMIES["gobelin"],
            ENEMIES["gobelin"]
        ],
        description="Quatre gobelins vous tendent une embuscade depuis les buissons!",
        difficulty="Facile",
        experience_reward=200
    ),
    "patrouille d'orcs": Combat(
        name="Patrouille d'orcs",
        enemies=[
            ENEMIES["orc"],
            ENEMIES["orc"],
            ENEMIES["orc"]
        ],
        description="Trois orcs armés vous bloquent le passage!",
        difficulty="Moyenne",
        experience_reward=450
    ),
    "meute de loups": Combat(
        name="Meute de loups",
        enemies=[
            ENEMIES["loup"],
            ENEMIES["loup"],
            ENEMIES["loup"],
            ENEMIES["loup"]
        ],
        description="Une meute de loups affamés vous attaque!",
        difficulty="Facile",
        experience_reward=220
    ),
    "cimetière hanté": Combat(
        name="Cimetière hanté",
        enemies=[
            ENEMIES["squelette"],
            ENEMIES["squelette"],
            ENEMIES["zombie"],
            ENEMIES["zombie"]
        ],
        description="Des morts-vivants se lèvent de leurs tombes pour vous attaquer!",
        difficulty="Moyenne",
        experience_reward=500
    ),
    "troll solitaire": Combat(
        name="Troll solitaire",
        enemies=[
            ENEMIES["troll"]
        ],
        description="Un troll monstrueux bloque votre chemin!",
        difficulty="Difficile",
        experience_reward=750
    ),
}


def get_combat_by_name(name: str) -> Optional[Combat]:
    """Get a combat encounter by its name"""
    return COMBAT_ENCOUNTERS.get(name.lower())
