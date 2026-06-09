"""
Scenario system for D&D
"""
import re
import random
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from .character import Character, Race, Class, Alignment, create_random_character
from .dice import Dice, DiceResult, roll_dice
from .item import Item, Weapon, Armor, Potion, get_item_by_name, get_random_item
from .spell import Spell, get_spell_by_name, get_random_spell
from .combat import Combat, Enemy, get_enemy_by_name, get_combat_by_name, get_random_enemy


class ScenarioEventType(Enum):
    """Types of scenario events"""
    TEXT = "texte"
    DIALOGUE = "dialogue"
    COMBAT = "combat"
    CHOICE = "choix"
    CHECK = "jet"
    REWARD = "récompense"
    TRAP = "piège"
    PUZZLE = "énigme"
    REST = "repos"
    END = "fin"


class ScenarioConditionType(Enum):
    """Types of scenario conditions"""
    ALWAYS = "toujours"
    CHARACTER_LEVEL = "niveau_personnage"
    CHARACTER_CLASS = "classe_personnage"
    CHARACTER_RACE = "race_personnage"
    ITEM_IN_INVENTORY = "objet_inventaire"
    ENEMY_DEFEATED = "ennemi_vaincu"
    HEALTH_BELOW = "pv_inférieurs"
    SKILL_CHECK = "jet_compétence"
    VARIABLE = "variable"


@dataclass
class ScenarioCondition:
    """Condition for scenario events"""
    condition_type: ScenarioConditionType
    value: str = ""
    target: str = ""  # Character name or other target
    comparison: str = "=="  # ==, !=, >, <, >=, <=
    
    def check(self, game_state: Dict) -> bool:
        """Check if condition is met"""
        if self.condition_type == ScenarioConditionType.ALWAYS:
            return True
        
        elif self.condition_type == ScenarioConditionType.CHARACTER_LEVEL:
            character = self._get_character(self.target, game_state)
            if character:
                if self.comparison == "==":
                    return character.level == int(self.value)
                elif self.comparison == ">":
                    return character.level > int(self.value)
                elif self.comparison == "<":
                    return character.level < int(self.value)
                elif self.comparison == ">=":
                    return character.level >= int(self.value)
                elif self.comparison == "<=":
                    return character.level <= int(self.value)
                elif self.comparison == "!=":
                    return character.level != int(self.value)
        
        elif self.condition_type == ScenarioConditionType.CHARACTER_CLASS:
            character = self._get_character(self.target, game_state)
            if character:
                return character.char_class.value.lower() == self.value.lower()
        
        elif self.condition_type == ScenarioConditionType.CHARACTER_RACE:
            character = self._get_character(self.target, game_state)
            if character:
                return character.race.value.lower() == self.value.lower()
        
        elif self.condition_type == ScenarioConditionType.ITEM_IN_INVENTORY:
            character = self._get_character(self.target, game_state)
            if character:
                return any(item.name.lower() == self.value.lower() for item in character.inventory)
        
        elif self.condition_type == ScenarioConditionType.ENEMY_DEFEATED:
            combat = game_state.get('current_combat')
            if combat:
                for enemy, _ in combat.enemies_in_combat:
                    if enemy.name.lower() == self.value.lower():
                        return enemy.is_defeated()
        
        elif self.condition_type == ScenarioConditionType.HEALTH_BELOW:
            character = self._get_character(self.target, game_state)
            if character:
                if self.comparison == "<":
                    return character.current_hp < int(self.value)
                elif self.comparison == "<=":
                    return character.current_hp <= int(self.value)
        
        elif self.condition_type == ScenarioConditionType.SKILL_CHECK:
            # This would be checked during the event, not here
            return False
        
        elif self.condition_type == ScenarioConditionType.VARIABLE:
            variables = game_state.get('variables', {})
            if self.target in variables:
                if self.comparison == "==":
                    return str(variables[self.target]) == self.value
                elif self.comparison == "!=":
                    return str(variables[self.target]) != self.value
                elif self.comparison == ">":
                    return float(variables[self.target]) > float(self.value)
                elif self.comparison == "<":
                    return float(variables[self.target]) < float(self.value)
                elif self.comparison == ">=":
                    return float(variables[self.target]) >= float(self.value)
                elif self.comparison == "<=":
                    return float(variables[self.target]) <= float(self.value)
        
        return False
    
    def _get_character(self, name: str, game_state: Dict) -> Optional[Character]:
        """Get character by name from game state"""
        characters = game_state.get('characters', [])
        for char in characters:
            if char.name.lower() == name.lower():
                return char
        return None


@dataclass
class ScenarioAction:
    """Action to perform when an event occurs"""
    action_type: str  # "text", "combat", "reward", "set_variable", "modify_character", etc.
    value: str = ""
    target: str = ""
    amount: int = 0
    
    def execute(self, game_state: Dict) -> str:
        """Execute the action and return result text"""
        if self.action_type == "text":
            return self.value
        
        elif self.action_type == "set_variable":
            if 'variables' not in game_state:
                game_state['variables'] = {}
            game_state['variables'][self.target] = self.value
            return f"Variable {self.target} définie à {self.value}"
        
        elif self.action_type == "modify_variable":
            if 'variables' not in game_state:
                game_state['variables'] = {}
            if self.target in game_state['variables']:
                try:
                    current = float(game_state['variables'][self.target])
                    new_value = current + self.amount
                    game_state['variables'][self.target] = new_value
                    return f"Variable {self.target} modifiée: {current} -> {new_value}"
                except:
                    return f"Erreur: Impossible de modifier {self.target}"
            else:
                game_state['variables'][self.target] = self.amount
                return f"Variable {self.target} créée avec la valeur {self.amount}"
        
        elif self.action_type == "add_item":
            character = self._get_character(self.target, game_state)
            if character:
                item = get_item_by_name(self.value)
                if item:
                    character.add_to_inventory(item)
                    return f"{character.name} reçoit {item.name}"
                else:
                    # Create a generic item
                    generic_item = Item(name=self.value, item_type=ItemType.MISC)
                    character.add_to_inventory(generic_item)
                    return f"{character.name} reçoit {self.value}"
        
        elif self.action_type == "remove_item":
            character = self._get_character(self.target, game_state)
            if character:
                for item in character.inventory[:]:
                    if item.name.lower() == self.value.lower():
                        character.remove_from_inventory(item)
                        return f"{item.name} retiré de l'inventaire de {character.name}"
        
        elif self.action_type == "add_gold":
            character = self._get_character(self.target, game_state)
            if character:
                character.gold += self.amount
                return f"{character.name} reçoit {self.amount} pièces d'or"
        
        elif self.action_type == "remove_gold":
            character = self._get_character(self.target, game_state)
            if character:
                character.gold = max(0, character.gold - self.amount)
                return f"{character.name} perd {self.amount} pièces d'or"
        
        elif self.action_type == "heal":
            character = self._get_character(self.target, game_state)
            if character:
                old_hp = character.current_hp
                character.heal(self.amount)
                return f"{character.name} récupère {self.amount} PV ({old_hp} -> {character.current_hp})"
        
        elif self.action_type == "damage":
            character = self._get_character(self.target, game_state)
            if character:
                old_hp = character.current_hp
                character.take_damage(self.amount)
                return f"{character.name} subit {self.amount} dégâts ({old_hp} -> {character.current_hp})"
        
        elif self.action_type == "add_experience":
            character = self._get_character(self.target, game_state)
            if character:
                character.experience += self.amount
                return f"{character.name} gagne {self.amount} points d'expérience"
        
        elif self.action_type == "level_up":
            character = self._get_character(self.target, game_state)
            if character:
                old_level = character.level
                character.level_up()
                return f"{character.name} passe au niveau {character.level} (était niveau {old_level})"
        
        elif self.action_type == "start_combat":
            combat = get_combat_by_name(self.value)
            if combat:
                game_state['current_combat'] = combat
                game_state['combat_started'] = False
                return f"Combat: {combat.description}"
            else:
                # Create a new combat with the specified enemy
                enemy = get_enemy_by_name(self.value)
                if enemy:
                    new_combat = Combat(
                        name=f"Combat contre {enemy.name}",
                        enemies=[enemy],
                        description=f"Un {enemy.name} apparaît!",
                        difficulty="Moyenne"
                    )
                    game_state['current_combat'] = new_combat
                    game_state['combat_started'] = False
                    return f"Combat: {new_combat.description}"
        
        elif self.action_type == "end_combat":
            game_state['current_combat'] = None
            game_state['combat_started'] = False
            return "Le combat est terminé."
        
        elif self.action_type == "add_spell":
            character = self._get_character(self.target, game_state)
            if character:
                spell = get_spell_by_name(self.value)
                if spell:
                    if self.value not in character.known_spells:
                        character.known_spells.append(self.value)
                        return f"{character.name} apprend le sort {spell.name}"
        
        elif self.action_type == "add_weapon":
            character = self._get_character(self.target, game_state)
            if character:
                weapon = get_item_by_name(self.value)
                if weapon and isinstance(weapon, Weapon):
                    character.equip_weapon(weapon)
                    character.add_to_inventory(weapon)
                    return f"{character.name} reçoit {weapon.name}"
        
        elif self.action_type == "add_armor":
            character = self._get_character(self.target, game_state)
            if character:
                armor = get_item_by_name(self.value)
                if armor and isinstance(armor, Armor):
                    character.equip_armor(armor)
                    character.add_to_inventory(armor)
                    return f"{character.name} reçoit {armor.name}"
        
        return ""
    
    def _get_character(self, name: str, game_state: Dict) -> Optional[Character]:
        """Get character by name from game state"""
        characters = game_state.get('characters', [])
        for char in characters:
            if char.name.lower() == name.lower():
                return char
        return None


@dataclass
class ScenarioChoice:
    """Choice option in scenario"""
    text: str
    next_event_id: str
    condition: Optional[ScenarioCondition] = None
    
    def is_available(self, game_state: Dict) -> bool:
        """Check if this choice is available"""
        if self.condition is None:
            return True
        return self.condition.check(game_state)


@dataclass
class ScenarioEvent:
    """Event in the scenario"""
    event_id: str
    event_type: ScenarioEventType
    title: str = ""
    text: str = ""
    conditions: List[ScenarioCondition] = field(default_factory=list)
    actions: List[ScenarioAction] = field(default_factory=list)
    choices: List[ScenarioChoice] = field(default_factory=list)
    next_event_id: str = ""
    combat_name: str = ""
    enemy_names: List[str] = field(default_factory=list)
    skill_check: str = ""  # Skill to check
    dc: int = 10  # Difficulty class
    success_event_id: str = ""
    failure_event_id: str = ""
    reward_items: List[str] = field(default_factory=list)
    reward_gold: int = 0
    reward_experience: int = 0
    
    def is_available(self, game_state: Dict) -> bool:
        """Check if this event is available"""
        if not self.conditions:
            return True
        
        for condition in self.conditions:
            if not condition.check(game_state):
                return False
        return True
    
    def execute(self, game_state: Dict, choice_index: int = -1) -> Tuple[str, Optional[str]]:
        """
        Execute the event and return (result_text, next_event_id)
        
        Args:
            game_state: Current game state
            choice_index: Index of chosen option (-1 for no choice)
            
        Returns:
            Tuple of (result text, next event ID or None)
        """
        result_parts = []
        
        # Execute actions
        for action in self.actions:
            result = action.execute(game_state)
            if result:
                result_parts.append(result)
        
        # Handle event-specific logic
        if self.event_type == ScenarioEventType.TEXT:
            if self.text:
                result_parts.append(self.text)
            next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.DIALOGUE:
            if self.text:
                result_parts.append(self.text)
            next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.COMBAT:
            if self.combat_name:
                combat = get_combat_by_name(self.combat_name)
                if combat:
                    game_state['current_combat'] = combat
                    game_state['combat_started'] = False
                    result_parts.append(f"Combat: {combat.description}")
            elif self.enemy_names:
                enemies = []
                for enemy_name in self.enemy_names:
                    enemy = get_enemy_by_name(enemy_name)
                    if enemy:
                        enemies.append(enemy)
                
                if enemies:
                    combat = Combat(
                        name=f"Combat contre {' et '.join([e.name for e in enemies])}",
                        enemies=enemies,
                        description=f"{' et '.join([e.name for e in enemies])} apparaissent!",
                        difficulty="Moyenne"
                    )
                    game_state['current_combat'] = combat
                    game_state['combat_started'] = False
                    result_parts.append(f"Combat: {combat.description}")
            
            next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.CHOICE:
            if choice_index >= 0 and choice_index < len(self.choices):
                chosen = self.choices[choice_index]
                if chosen.is_available(game_state):
                    next_id = chosen.next_event_id
                else:
                    next_id = self.next_event_id if self.next_event_id else None
            else:
                next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.CHECK:
            # Perform skill check
            characters = game_state.get('characters', [])
            if characters:
                # Use first character for the check
                character = characters[0]
                result, _ = character.roll_skill_check(self.skill_check)
                
                result_parts.append(f"Jet de {self.skill_check}: {result.value} (DD {self.dc})")
                
                if result.value >= self.dc:
                    result_parts.append("Réussite!")
                    next_id = self.success_event_id if self.success_event_id else self.next_event_id
                else:
                    result_parts.append("Échec!")
                    next_id = self.failure_event_id if self.failure_event_id else self.next_event_id
            else:
                next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.REWARD:
            # Add rewards
            characters = game_state.get('characters', [])
            if characters:
                # Distribute items to first character (or all)
                for item_name in self.reward_items:
                    item = get_item_by_name(item_name)
                    if item:
                        characters[0].add_to_inventory(item)
                        result_parts.append(f"Vous recevez: {item.name}")
                    else:
                        result_parts.append(f"Vous recevez: {item_name}")
                
                # Add gold
                if self.reward_gold > 0:
                    characters[0].gold += self.reward_gold
                    result_parts.append(f"Vous recevez {self.reward_gold} pièces d'or")
                
                # Add experience
                if self.reward_experience > 0:
                    for char in characters:
                        char.experience += self.reward_experience
                    result_parts.append(f"Chaque personnage gagne {self.reward_experience} points d'expérience")
            
            next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.TRAP:
            # Trap logic
            characters = game_state.get('characters', [])
            if characters:
                # Check for perception or investigation
                result, _ = characters[0].roll_skill_check("perception", dc=self.dc)
                
                if result.value >= self.dc:
                    result_parts.append(f"Vous détectez le piège à temps! (Perception: {result.value} vs DD {self.dc})")
                    next_id = self.success_event_id if self.success_event_id else self.next_event_id
                else:
                    # Trap triggers
                    damage = roll_dice("2d6").value
                    for char in characters:
                        char.take_damage(damage)
                    result_parts.append(f"Le piège se déclenche! Chaque personnage subit {damage} dégâts.")
                    next_id = self.failure_event_id if self.failure_event_id else self.next_event_id
            else:
                next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.REST:
            characters = game_state.get('characters', [])
            for char in characters:
                # Short rest - recover HP equal to level
                healed = char.level
                char.heal(healed)
                result_parts.append(f"{char.name} récupère {healed} PV après un repos court")
            
            next_id = self.next_event_id if self.next_event_id else None
        
        elif self.event_type == ScenarioEventType.END:
            result_parts.append(self.text if self.text else "Fin du scénario.")
            next_id = None
        
        else:
            next_id = self.next_event_id if self.next_event_id else None
        
        return "\n\n".join(result_parts), next_id


class ScenarioParser:
    """Parser for scenario files"""
    
    @staticmethod
    def parse_scenario_file(file_path: str) -> 'Scenario':
        """Parse a scenario from a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return ScenarioParser.parse_scenario_content(content)
    
    @staticmethod
    def parse_scenario_content(content: str) -> 'Scenario':
        """Parse scenario from string content"""
        # This is a simplified parser for a custom scenario format
        # Format:
        # [scenario]
        # title: Nom du scénario
        # description: Description
        # author: Auteur
        # 
        # [event:start]
        # type: text
        # title: Bienvenue
        # text: Bienvenue dans cette aventure!
        # next: event1
        # 
        # [event:event1]
        # type: choice
        # text: Que faites-vous?
        # choice1: Explorer la forêt -> event2
        # choice2: Retourner au village -> event3
        
        scenario = Scenario(
            title="Scénario sans titre",
            description="",
            events={}
        )
        
        current_event = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Scenario header
            if line.startswith('[scenario]'):
                current_event = None
                continue
            elif current_event is None and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'title':
                    scenario.title = value
                elif key == 'description':
                    scenario.description = value
                elif key == 'author':
                    scenario.author = value
                continue
            
            # Event header
            if line.startswith('[event:'):
                event_id = line[7:-1].strip()
                current_event = ScenarioEvent(
                    event_id=event_id,
                    event_type=ScenarioEventType.TEXT,
                    title="",
                    text="",
                    conditions=[],
                    actions=[],
                    choices=[],
                    next_event_id=""
                )
                scenario.events[event_id] = current_event
                continue
            
            if current_event is None:
                continue
            
            # Event properties
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'type':
                    event_type = value.lower()
                    if event_type == 'text':
                        current_event.event_type = ScenarioEventType.TEXT
                    elif event_type == 'dialogue':
                        current_event.event_type = ScenarioEventType.DIALOGUE
                    elif event_type == 'combat':
                        current_event.event_type = ScenarioEventType.COMBAT
                    elif event_type == 'choice':
                        current_event.event_type = ScenarioEventType.CHOICE
                    elif event_type == 'check':
                        current_event.event_type = ScenarioEventType.CHECK
                    elif event_type == 'reward':
                        current_event.event_type = ScenarioEventType.REWARD
                    elif event_type == 'trap':
                        current_event.event_type = ScenarioEventType.TRAP
                    elif event_type == 'puzzle':
                        current_event.event_type = ScenarioEventType.PUZZLE
                    elif event_type == 'rest':
                        current_event.event_type = ScenarioEventType.REST
                    elif event_type == 'end':
                        current_event.event_type = ScenarioEventType.END
                
                elif key == 'title':
                    current_event.title = value
                elif key == 'text':
                    current_event.text = value
                elif key == 'next':
                    current_event.next_event_id = value
                elif key == 'combat':
                    current_event.combat_name = value
                elif key == 'enemies':
                    current_event.enemy_names = [e.strip() for e in value.split(',')]
                elif key == 'skill':
                    current_event.skill_check = value
                elif key == 'dc':
                    current_event.dc = int(value)
                elif key == 'success':
                    current_event.success_event_id = value
                elif key == 'failure':
                    current_event.failure_event_id = value
                elif key == 'reward_items':
                    current_event.reward_items = [item.strip() for item in value.split(',')]
                elif key == 'reward_gold':
                    current_event.reward_gold = int(value)
                elif key == 'reward_xp':
                    current_event.reward_experience = int(value)
                
                # Choices
                elif key.startswith('choice'):
                    choice_text, next_event = value.split('->', 1)
                    choice_text = choice_text.strip()
                    next_event = next_event.strip()
                    current_event.choices.append(ScenarioChoice(
                        text=choice_text,
                        next_event_id=next_event
                    ))
                
                # Conditions (simplified)
                elif key == 'condition':
                    # Format: type:value:target:comparison
                    parts = value.split(':')
                    if len(parts) >= 2:
                        cond_type = parts[0].strip().lower()
                        cond_value = parts[1].strip() if len(parts) > 1 else ""
                        cond_target = parts[2].strip() if len(parts) > 2 else ""
                        cond_comparison = parts[3].strip() if len(parts) > 3 else "=="
                        
                        condition = ScenarioCondition(
                            condition_type=ScenarioConditionType.ALWAYS,
                            value=cond_value,
                            target=cond_target,
                            comparison=cond_comparison
                        )
                        
                        # Map condition types
                        if cond_type == 'level':
                            condition.condition_type = ScenarioConditionType.CHARACTER_LEVEL
                        elif cond_type == 'class':
                            condition.condition_type = ScenarioConditionType.CHARACTER_CLASS
                        elif cond_type == 'race':
                            condition.condition_type = ScenarioConditionType.CHARACTER_RACE
                        elif cond_type == 'item':
                            condition.condition_type = ScenarioConditionType.ITEM_IN_INVENTORY
                        elif cond_type == 'enemy_defeated':
                            condition.condition_type = ScenarioConditionType.ENEMY_DEFEATED
                        elif cond_type == 'health':
                            condition.condition_type = ScenarioConditionType.HEALTH_BELOW
                        elif cond_type == 'variable':
                            condition.condition_type = ScenarioConditionType.VARIABLE
                        
                        current_event.conditions.append(condition)
                
                # Actions
                elif key == 'action':
                    # Format: type:value:target:amount
                    parts = value.split(':')
                    if len(parts) >= 1:
                        action_type = parts[0].strip().lower()
                        action_value = parts[1].strip() if len(parts) > 1 else ""
                        action_target = parts[2].strip() if len(parts) > 2 else ""
                        action_amount = int(parts[3].strip()) if len(parts) > 3 else 0
                        
                        action = ScenarioAction(
                            action_type=action_type,
                            value=action_value,
                            target=action_target,
                            amount=action_amount
                        )
                        current_event.actions.append(action)
        
        # Set start event if not set
        if 'start' not in scenario.events and scenario.events:
            scenario.start_event_id = list(scenario.events.keys())[0]
        
        return scenario


@dataclass
class Scenario:
    """D&D Scenario class"""
    title: str
    description: str = ""
    author: str = ""
    version: str = "1.0"
    start_event_id: str = "start"
    events: Dict[str, ScenarioEvent] = field(default_factory=dict)
    
    # Current state
    current_event_id: str = ""
    
    def start(self) -> ScenarioEvent:
        """Start the scenario"""
        self.current_event_id = self.start_event_id
        return self.get_current_event()
    
    def get_current_event(self) -> Optional[ScenarioEvent]:
        """Get the current event"""
        return self.events.get(self.current_event_id)
    
    def go_to_event(self, event_id: str) -> Optional[ScenarioEvent]:
        """Go to a specific event"""
        if event_id in self.events:
            self.current_event_id = event_id
            return self.events[event_id]
        return None
    
    def next_event(self, game_state: Dict, choice_index: int = -1) -> Tuple[str, Optional[str]]:
        """
        Move to next event and return result
        
        Args:
            game_state: Current game state
            choice_index: Index of chosen option
            
        Returns:
            Tuple of (result text, next event ID or None)
        """
        current_event = self.get_current_event()
        if not current_event:
            return "Événement introuvable", None
        
        # Execute current event
        result_text, next_event_id = current_event.execute(game_state, choice_index)
        
        # Move to next event
        if next_event_id:
            self.current_event_id = next_event_id
        else:
            self.current_event_id = ""
        
        return result_text, next_event_id
    
    def get_available_choices(self, game_state: Dict) -> List[ScenarioChoice]:
        """Get available choices for current event"""
        current_event = self.get_current_event()
        if not current_event or current_event.event_type != ScenarioEventType.CHOICE:
            return []
        
        return [choice for choice in current_event.choices if choice.is_available(game_state)]
    
    def get_scenario_summary(self) -> str:
        """Get a summary of the scenario"""
        summary = []
        summary.append(f"Scénario: {self.title}")
        if self.author:
            summary.append(f"Auteur: {self.author}")
        if self.description:
            summary.append(f"Description: {self.description}")
        summary.append(f"Nombre d'événements: {len(self.events)}")
        summary.append(f"Événement de départ: {self.start_event_id}")
        
        return "\n".join(summary)


def create_sample_scenario() -> Scenario:
    """Create a sample scenario for testing"""
    scenario = Scenario(
        title="La Forêt Interdite",
        description="Une aventure dans une forêt mystérieuse remplie de dangers et de trésors.",
        author="Maître du Jeu Virtuel",
        start_event_id="start"
    )
    
    # Start event
    start_event = ScenarioEvent(
        event_id="start",
        event_type=ScenarioEventType.TEXT,
        title="Début de l'aventure",
        text="Vous entrez dans la Forêt Interdite, un lieu légendaire rempli de mystères et de dangers. "
             "Les arbres sont hauts et sombres, et l'air est lourd de magie ancienne. "
             "Devant vous, un sentier se divise en deux directions.",
        next_event_id="path_choice"
    )
    scenario.events["start"] = start_event
    
    # Path choice
    path_choice = ScenarioEvent(
        event_id="path_choice",
        event_type=ScenarioEventType.CHOICE,
        title="Choix du chemin",
        text="Quel chemin prenez-vous?",
        choices=[
            ScenarioChoice(
                text="Prendre le sentier de gauche, qui semble plus sombre et mystérieux",
                next_event_id="left_path"
            ),
            ScenarioChoice(
                text="Prendre le sentier de droite, qui semble plus éclairé et sûr",
                next_event_id="right_path"
            ),
            ScenarioChoice(
                text="Explorer les buissons à côté du sentier",
                next_event_id="bushes"
            )
        ]
    )
    scenario.events["path_choice"] = path_choice
    
    # Left path - leads to combat
    left_path = ScenarioEvent(
        event_id="left_path",
        event_type=ScenarioEventType.TEXT,
        title="Le sentier sombre",
        text="Vous prenez le sentier de gauche. Au fur et à mesure que vous avancez, "
             "l'obscurité devient plus épaisse. Soudain, vous entendez des bruits de pas derrière vous!\n\n"
             "Quatre gobelins surgissent des ombres, armés de cimeterres et d'arcs courts!",
        next_event_id="goblin_combat"
    )
    scenario.events["left_path"] = left_path
    
    # Goblin combat
    goblin_combat = ScenarioEvent(
        event_id="goblin_combat",
        event_type=ScenarioEventType.COMBAT,
        title="Combat contre les gobelins",
        combat_name="embuscade de gobelins",
        next_event_id="after_goblin_combat"
    )
    scenario.events["goblin_combat"] = goblin_combat
    
    # After goblin combat
    after_goblin_combat = ScenarioEvent(
        event_id="after_goblin_combat",
        event_type=ScenarioEventType.REWARD,
        title="Victoire!",
        text="Vous avez vaincu les gobelins! En fouillant leurs corps, vous trouvez quelques objets.",
        reward_items=["épée courte", "potion de soins"],
        reward_gold=50,
        reward_experience=200,
        next_event_id="treasure_chest"
    )
    scenario.events["after_goblin_combat"] = after_goblin_combat
    
    # Treasure chest
    treasure_chest = ScenarioEvent(
        event_id="treasure_chest",
        event_type=ScenarioEventType.CHOICE,
        title="Un coffre au trésor",
        text="Derrière les gobelins, vous trouvez un coffre en bois rouillé. Il semble verrouillé.",
        choices=[
            ScenarioChoice(
                text="Essayer de forcer le coffre",
                next_event_id="force_chest"
            ),
            ScenarioChoice(
                text="Chercher une clé sur les gobelins",
                next_event_id="search_key"
            ),
            ScenarioChoice(
                text="Laisser le coffre et continuer",
                next_event_id="continue_path"
            )
        ]
    )
    scenario.events["treasure_chest"] = treasure_chest
    
    # Force chest
    force_chest = ScenarioEvent(
        event_id="force_chest",
        event_type=ScenarioEventType.CHECK,
        title="Forcer le coffre",
        text="Vous tentez de forcer le coffre avec vos outils...",
        skill_check="athletics",
        dc=15,
        success_event_id="chest_success",
        failure_event_id="chest_trap"
    )
    scenario.events["force_chest"] = force_chest
    
    # Chest success
    chest_success = ScenarioEvent(
        event_id="chest_success",
        event_type=ScenarioEventType.REWARD,
        title="Succès!",
        text="Avec un grand effort, vous parvez à ouvrir le coffre! À l'intérieur, vous trouvez:",
        reward_items=["épée longue", "armure de cuir clouté"],
        reward_gold=100,
        next_event_id="continue_path"
    )
    scenario.events["chest_success"] = chest_success
    
    # Chest trap
    chest_trap = ScenarioEvent(
        event_id="chest_trap",
        event_type=ScenarioEventType.TRAP,
        title="Piège!",
        text="En forçant le coffre, vous déclenchez un mécanisme! Une lame jaillit du coffre!",
        dc=14,
        success_event_id="chest_success",
        failure_event_id="chest_trap_hit"
    )
    scenario.events["chest_trap"] = chest_trap
    
    # Chest trap hit
    chest_trap_hit = ScenarioEvent(
        event_id="chest_trap_hit",
        event_type=ScenarioEventType.TEXT,
        title="Blessé!",
        text="La lame vous transperce! Vous subissez des dégâts mais le coffre s'ouvre.",
        next_event_id="chest_success"
    )
    scenario.events["chest_trap_hit"] = chest_trap_hit
    
    # Search key
    search_key = ScenarioEvent(
        event_id="search_key",
        event_type=ScenarioEventType.CHECK,
        title="Chercher une clé",
        text="Vous fouillez les corps des gobelins à la recherche d'une clé...",
        skill_check="investigation",
        dc=12,
        success_event_id="key_found",
        failure_event_id="no_key"
    )
    scenario.events["search_key"] = search_key
    
    # Key found
    key_found = ScenarioEvent(
        event_id="key_found",
        event_type=ScenarioEventType.TEXT,
        title="Clé trouvée!",
        text="Vous trouvez une petite clé en fer sur le corps d'un gobelin. Elle ouvre le coffre!",
        next_event_id="chest_success"
    )
    scenario.events["key_found"] = key_found
    
    # No key
    no_key = ScenarioEvent(
        event_id="no_key",
        event_type=ScenarioEventType.TEXT,
        title="Pas de clé",
        text="Après une recherche minutieuse, vous ne trouvez pas de clé. Le coffre reste verrouillé.",
        next_event_id="continue_path"
    )
    scenario.events["no_key"] = no_key
    
    # Continue path
    continue_path = ScenarioEvent(
        event_id="continue_path",
        event_type=ScenarioEventType.TEXT,
        title="Continuer le chemin",
        text="Vous continuez votre chemin dans la forêt. Après quelques heures de marche, "
             "vous arrivez à une clairière avec une ancienne pierre runique au centre.",
        next_event_id="runestone"
    )
    scenario.events["continue_path"] = continue_path
    
    # Runestone
    runestone = ScenarioEvent(
        event_id="runestone",
        event_type=ScenarioEventType.CHOICE,
        title="La pierre runique",
        text="La pierre est couverte de runes anciennes. Elle semble pulsée d'une énergie magique.",
        choices=[
            ScenarioChoice(
                text="Toucher la pierre pour activer sa magie",
                next_event_id="touch_stone"
            ),
            ScenarioChoice(
                text="Étudier les runes de plus près",
                next_event_id="study_runes"
            ),
            ScenarioChoice(
                text="Ignorer la pierre et continuer",
                next_event_id="leave_stone"
            )
        ]
    )
    scenario.events["runestone"] = runestone
    
    # Touch stone
    touch_stone = ScenarioEvent(
        event_id="touch_stone",
        event_type=ScenarioEventType.COMBAT,
        title="Réveil de la pierre",
        text="En touchant la pierre, vous déclenchez un ancien sort de protection! "
             "La pierre prend vie et un golem de pierre apparaît devant vous!",
        enemy_names=["golem de pierre"],
        next_event_id="after_stone_combat"
    )
    scenario.events["touch_stone"] = touch_stone
    
    # After stone combat
    after_stone_combat = ScenarioEvent(
        event_id="after_stone_combat",
        event_type=ScenarioEventType.REWARD,
        title="Victoire contre le golem",
        text="Vous avez vaincu le golem de pierre! La pierre runique s'éteint et révèle un passage secret.",
        reward_items=["potion de soins supérieurs", "bâton magique"],
        reward_gold=200,
        reward_experience=500,
        next_event_id="secret_passage"
    )
    scenario.events["after_stone_combat"] = after_stone_combat
    
    # Secret passage
    secret_passage = ScenarioEvent(
        event_id="secret_passage",
        event_type=ScenarioEventType.TEXT,
        title="Passage secret",
        text="Le passage secret mène à une chambre cachée. Au centre, vous trouvez un autel "
             "avec une épée légendaire posée dessus. C'est la célèbre Épée du Dragon!",
        next_event_id="final_choice"
    )
    scenario.events["secret_passage"] = secret_passage
    
    # Final choice
    final_choice = ScenarioEvent(
        event_id="final_choice",
        event_type=ScenarioEventType.CHOICE,
        title="L'Épée du Dragon",
        text="L'épée brille d'une lumière intense. Prendre cette arme pourrait changer votre destin.",
        choices=[
            ScenarioChoice(
                text="Prendre l'épée et l'emmener avec vous",
                next_event_id="take_sword"
            ),
            ScenarioChoice(
                text="Laisser l'épée ici, c'est trop dangereux",
                next_event_id="leave_sword"
            )
        ]
    )
    scenario.events["final_choice"] = final_choice
    
    # Take sword
    take_sword = ScenarioEvent(
        event_id="take_sword",
        event_type=ScenarioEventType.REWARD,
        title="L'Épée est à vous!",
        text="Vous prenez l'Épée du Dragon. Une vague de pouvoir vous traverse. "
             "Vous sentez que cette arme sera votre compagne pour de nombreuses aventures.",
        reward_items=["Épée du Dragon"],
        reward_experience=1000,
        next_event_id="end_good"
    )
    scenario.events["take_sword"] = take_sword
    
    # Leave sword
    leave_sword = ScenarioEvent(
        event_id="leave_sword",
        event_type=ScenarioEventType.TEXT,
        title="Sagesse",
        text="Vous décidez de laisser l'épée. Parfois, la sagesse vaut plus que le pouvoir. "
             "Vous quittez la forêt avec un sentiment de paix.",
        next_event_id="end_neutral"
    )
    scenario.events["leave_sword"] = leave_sword
    
    # Right path
    right_path = ScenarioEvent(
        event_id="right_path",
        event_type=ScenarioEventType.TEXT,
        title="Le sentier éclairé",
        text="Vous prenez le sentier de droite. La lumière du soleil filtre à travers les feuilles, "
             "créant un environnement paisible. Après une heure de marche, vous arrivez à une rivière.",
        next_event_id="river"
    )
    scenario.events["right_path"] = right_path
    
    # River
    river = ScenarioEvent(
        event_id="river",
        event_type=ScenarioEventType.CHOICE,
        title="La rivière",
        text="La rivière est large mais peu profonde. Vous pouvez essayer de la traverser.",
        choices=[
            ScenarioChoice(
                text="Traverser la rivière à gué",
                next_event_id="cross_river"
            ),
            ScenarioChoice(
                text="Suivre la rivière jusqu'à un pont",
                next_event_id="follow_river"
            ),
            ScenarioChoice(
                text="Faire un repos près de la rivière",
                next_event_id="rest_river"
            )
        ]
    )
    scenario.events["river"] = river
    
    # Cross river
    cross_river = ScenarioEvent(
        event_id="cross_river",
        event_type=ScenarioEventType.CHECK,
        title="Traverser la rivière",
        text="Vous commencez à traverser la rivière...",
        skill_check="athletics",
        dc=10,
        success_event_id="cross_success",
        failure_event_id="cross_failure"
    )
    scenario.events["cross_river"] = cross_river
    
    # Cross success
    cross_success = ScenarioEvent(
        event_id="cross_success",
        event_type=ScenarioEventType.TEXT,
        title="Traversée réussie",
        text="Vous traversez la rivière sans problème. De l'autre côté, vous trouvez un chemin qui mène hors de la forêt.",
        next_event_id="end_neutral"
    )
    scenario.events["cross_success"] = cross_success
    
    # Cross failure
    cross_failure = ScenarioEvent(
        event_id="cross_failure",
        event_type=ScenarioEventType.TEXT,
        title="Chute dans la rivière",
        text="Vous glissez sur une pierre moussue et tombez dans la rivière! "
             "Vous perdez un peu d'équipement mais vous vous en sortez sain et sauf.",
        next_event_id="end_bad"
    )
    scenario.events["cross_failure"] = cross_failure
    
    # Follow river
    follow_river = ScenarioEvent(
        event_id="follow_river",
        event_type=ScenarioEventType.TEXT,
        title="Suivre la rivière",
        text="Vous suivez la rivière pendant plusieurs heures. Finalement, vous arrivez à un petit village. "
             "Les habitants vous accueillent chaleureusement.",
        next_event_id="village"
    )
    scenario.events["follow_river"] = follow_river
    
    # Village
    village = ScenarioEvent(
        event_id="village",
        event_type=ScenarioEventType.REWARD,
        title="Arrivée au village",
        text="Le maire du village vous remercie de votre visite et vous offre une récompense pour vos efforts.",
        reward_gold=100,
        reward_experience=150,
        next_event_id="end_good"
    )
    scenario.events["village"] = village
    
    # Rest at river
    rest_river = ScenarioEvent(
        event_id="rest_river",
        event_type=ScenarioEventType.REST,
        title="Repos près de la rivière",
        text="Vous faites une pause bien méritée près de la rivière. L'eau fraîche et le chant des oiseaux vous revitalisent.",
        next_event_id="after_rest"
    )
    scenario.events["rest_river"] = rest_river
    
    # After rest
    after_rest = ScenarioEvent(
        event_id="after_rest",
        event_type=ScenarioEventType.TEXT,
        title="Après le repos",
        text="Rafraîchis, vous continuez votre voyage. La forêt semble moins menaçante maintenant.",
        next_event_id="end_good"
    )
    scenario.events["after_rest"] = after_rest
    
    # Bushes
    bushes = ScenarioEvent(
        event_id="bushes",
        event_type=ScenarioEventType.CHECK,
        title="Explorer les buissons",
        text="Vous vous aventurez dans les buissons épais...",
        skill_check="perception",
        dc=12,
        success_event_id="bushes_success",
        failure_event_id="bushes_failure"
    )
    scenario.events["bushes"] = bushes
    
    # Bushes success
    bushes_success = ScenarioEvent(
        event_id="bushes_success",
        event_type=ScenarioEventType.REWARD,
        title="Découverte!",
        text="Vous trouvez un petit sac caché dans les buissons! Il contient:",
        reward_items=["potion de soins", "potion de force"],
        reward_gold=30,
        next_event_id="continue_path"
    )
    scenario.events["bushes_success"] = bushes_success
    
    # Bushes failure
    bushes_failure = ScenarioEvent(
        event_id="bushes_failure",
        event_type=ScenarioEventType.TRAP,
        title="Piège!",
        text="Vous déclenchez un piège caché! Un filet tombe des arbres et vous capture!",
        dc=15,
        success_event_id="bushes_escape",
        failure_event_id="bushes_caught"
    )
    scenario.events["bushes_failure"] = bushes_failure
    
    # Bushes escape
    bushes_escape = ScenarioEvent(
        event_id="bushes_escape",
        event_type=ScenarioEventType.TEXT,
        title="Échappée!",
        text="Vous parvez à éviter le piège au dernier moment!",
        next_event_id="continue_path"
    )
    scenario.events["bushes_escape"] = bushes_escape
    
    # Bushes caught
    bushes_caught = ScenarioEvent(
        event_id="bushes_caught",
        event_type=ScenarioEventType.TEXT,
        title="Capturé!",
        text="Vous êtes capturé par le piège! Il vous faut du temps pour vous libérer.",
        next_event_id="end_bad"
    )
    scenario.events["bushes_caught"] = bushes_caught
    
    # End events
    end_good = ScenarioEvent(
        event_id="end_good",
        event_type=ScenarioEventType.END,
        title="Fin - Victoire!",
        text="Félicitations! Vous avez complété votre aventure dans la Forêt Interdite avec succès. "
             "Vos actions héroïques seront racontées pendant des générations!"
    )
    scenario.events["end_good"] = end_good
    
    end_neutral = ScenarioEvent(
        event_id="end_neutral",
        event_type=ScenarioEventType.END,
        title="Fin - Aventure terminée",
        text="Votre aventure dans la Forêt Interdite touche à sa fin. "
             "Vous avez survécu et appris de nouvelles choses sur vous-même."
    )
    scenario.events["end_neutral"] = end_neutral
    
    end_bad = ScenarioEvent(
        event_id="end_bad",
        event_type=ScenarioEventType.END,
        title="Fin - Défaite",
        text="Votre aventure se termine ici. La Forêt Interdite vous a vaincu, "
             "mais ne désespérez pas - chaque échec est une leçon pour la prochaine fois."
    )
    scenario.events["end_bad"] = end_bad
    
    return scenario


# Add stone golem enemy for the sample scenario
from .combat import ENEMIES, EnemyType, EnemySize
ENEMIES["golem de pierre"] = Enemy(
    name="Golem de pierre",
    enemy_type=EnemyType.CONSTRUCT,
    size=EnemySize.LARGE,
    armor_class=17,
    hit_points=178,
    speed=30,
    strength=20,
    dexterity=8,
    constitution=20,
    intelligence=6,
    wisdom=10,
    charisma=5,
    challenge_rating=10,
    proficiency_bonus=4,
    multiattack=True,
    actions=[
        "Attaques multiples. Le golem effectue deux attaques de coup.",
        "Coup. Attaque de mêlée: +8, portée 5 pieds, une cible. Touché: 19 (3d8+6) dégâts contondants."
    ],
    damage_resistances=["contondant", "perforant", "tranchant"],
    damage_immunities=["poison", "psychique"],
    condition_immunities=["charme", "effrayé", "empoisonné", "épuisé", "paralysé", "pétrifié"],
    senses=["vision dans le noir 18 m", "perception passive 10"],
    passive_perception=10,
    languages="comprend les langues de son créateur mais ne peut pas parler"
)
