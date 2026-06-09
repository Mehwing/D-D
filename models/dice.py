"""
Dice rolling system for D&D
"""
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DiceResult:
    """Result of a dice roll"""
    dice_type: str
    value: int
    is_critical: bool = False
    is_fumble: bool = False


class Dice:
    """Dice class for rolling various D&D dice"""
    
    DICE_TYPES = {
        'd4': 4,
        'd6': 6,
        'd8': 8,
        'd10': 10,
        'd12': 12,
        'd20': 20,
        'd100': 100
    }
    
    @staticmethod
    def roll(dice_type: str, count: int = 1, modifier: int = 0) -> DiceResult:
        """
        Roll a dice of specified type
        
        Args:
            dice_type: Type of dice (d4, d6, d8, d10, d12, d20, d100)
            count: Number of dice to roll
            modifier: Modifier to add to the result
            
        Returns:
            DiceResult object
        """
        if dice_type not in Dice.DICE_TYPES:
            raise ValueError(f"Invalid dice type: {dice_type}")
        
        sides = Dice.DICE_TYPES[dice_type]
        
        # Roll the dice
        if count == 1:
            value = random.randint(1, sides) + modifier
        else:
            # For multiple dice, return sum
            total = sum(random.randint(1, sides) for _ in range(count))
            value = total + modifier
        
        # Check for critical/fumble (only for d20)
        is_critical = False
        is_fumble = False
        
        if dice_type == 'd20' and count == 1:
            raw_roll = value - modifier
            is_critical = raw_roll == 20
            is_fumble = raw_roll == 1
        
        return DiceResult(
            dice_type=dice_type,
            value=value,
            is_critical=is_critical,
            is_fumble=is_fumble
        )
    
    @staticmethod
    def roll_multiple(dice_specs: List[Tuple[str, int, int]]) -> List[DiceResult]:
        """
        Roll multiple different dice
        
        Args:
            dice_specs: List of (dice_type, count, modifier) tuples
            
        Returns:
            List of DiceResult objects
        """
        results = []
        for dice_type, count, modifier in dice_specs:
            results.append(Dice.roll(dice_type, count, modifier))
        return results


def roll_dice(dice_notation: str) -> DiceResult:
    """
    Parse and roll dice from notation like "1d20", "2d6+3", "d100"
    
    Args:
        dice_notation: String notation for dice roll
        
    Returns:
            DiceResult object
    """
    # Parse the notation
    notation = dice_notation.lower().strip()
    
    # Default values
    count = 1
    dice_type = 'd20'
    modifier = 0
    
    # Handle simple cases
    if notation == 'd20':
        return Dice.roll('d20')
    elif notation == 'd100':
        return Dice.roll('d100')
    
    # Parse complex notation
    if 'd' in notation:
        parts = notation.split('d')
        if parts[0]:
            count = int(parts[0])
        
        rest = parts[1]
        # Check for modifier
        if '+' in rest:
            dice_part, mod_part = rest.split('+')
            dice_type = f'd{dice_part}'
            modifier = int(mod_part)
        elif '-' in rest:
            dice_part, mod_part = rest.split('-')
            dice_type = f'd{dice_part}'
            modifier = -int(mod_part)
        else:
            dice_type = f'd{rest}'
    
    return Dice.roll(dice_type, count, modifier)


def roll_advantage(dice_type: str = 'd20', modifier: int = 0) -> Tuple[DiceResult, DiceResult, DiceResult]:
    """
    Roll with advantage (roll 2d20, take highest)
    
    Returns:
        Tuple of (result, first_roll, second_roll)
    """
    roll1 = Dice.roll(dice_type, 1, modifier)
    roll2 = Dice.roll(dice_type, 1, modifier)
    
    if roll1.value >= roll2.value:
        best = roll1
    else:
        best = roll2
    
    return best, roll1, roll2


def roll_disadvantage(dice_type: str = 'd20', modifier: int = 0) -> Tuple[DiceResult, DiceResult, DiceResult]:
    """
    Roll with disadvantage (roll 2d20, take lowest)
    
    Returns:
        Tuple of (result, first_roll, second_roll)
    """
    roll1 = Dice.roll(dice_type, 1, modifier)
    roll2 = Dice.roll(dice_type, 1, modifier)
    
    if roll1.value <= roll2.value:
        worst = roll1
    else:
        worst = roll2
    
    return worst, roll1, roll2
