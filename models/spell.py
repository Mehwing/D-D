"""
Spell system for D&D
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .dice import Dice, DiceResult


class SpellSchool(Enum):
    """Schools of magic"""
    ABJURATION = "Abjuration"
    CONJURATION = "Conjuration"
    DIVINATION = "Divination"
    ENCHANTMENT = "Enchantement"
    EVOCATION = "Évocation"
    ILLUSION = "Illusion"
    NECROMANCY = "Nécromancie"
    TRANSMUTATION = "Transmutation"


class SpellComponent(Enum):
    """Spell components"""
    VERBAL = "Verbal"
    SOMATIC = "Somatique"
    MATERIAL = "Matériel"


@dataclass
class Spell:
    """Spell class"""
    name: str
    school: SpellSchool
    level: int = 0  # 0 for cantrip
    casting_time: str = "1 action"
    range: str = "30 pieds"
    components: List[SpellComponent] = field(default_factory=list)
    duration: str = "Instantané"
    description: str = ""
    effect: str = ""
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    save: Optional[str] = None  # Saving throw (STR, DEX, CON, INT, WIS, CHA)
    attack_type: Optional[str] = None  # "ranged" or "melee"
    ritual: bool = False
    concentration: bool = False
    
    def __str__(self) -> str:
        return f"{self.name} ({self.school.value}, niveau {self.level})"
    
    def get_full_description(self) -> str:
        """Get full spell description"""
        desc = []
        desc.append(f"{self.name}")
        desc.append(f"École: {self.school.value}, Niveau: {self.level}")
        desc.append(f"Temps d'incantation: {self.casting_time}")
        desc.append(f"Portée: {self.range}")
        
        components = []
        if SpellComponent.VERBAL in self.components:
            components.append("V")
        if SpellComponent.SOMATIC in self.components:
            components.append("S")
        if SpellComponent.MATERIAL in self.components:
            components.append("M")
        desc.append(f"Composantes: {', '.join(components)}")
        
        desc.append(f"Durée: {self.duration}")
        
        if self.damage_dice:
            desc.append(f"Dégâts: {self.damage_dice} {self.damage_type}")
        
        if self.save:
            desc.append(f"Jet de sauvegarde: {self.save}")
        
        if self.concentration:
            desc.append("Concentration requise")
        
        if self.ritual:
            desc.append("Rituel")
        
        desc.append("")
        desc.append(self.description)
        
        return "\n".join(desc)
    
    def cast(self, caster_level: int, spell_slot: Optional[int] = None) -> str:
        """Cast the spell and return the effect"""
        if self.level > 0 and spell_slot is None:
            return f"Échec: Emplacement de sort de niveau {self.level} requis"
        
        if self.level > 0 and (spell_slot is None or spell_slot < self.level):
            return f"Échec: Emplacement de sort de niveau {self.level} minimum requis"
        
        # Roll damage if applicable
        if self.damage_dice:
            damage_result = Dice.roll(self.damage_dice)
            # Add caster level bonus for some spells
            if self.level > 0:
                damage_result.value += caster_level // 2
            return f"{self.name} inflige {damage_result.value} dégâts {self.damage_type}! {self.effect}"
        
        return f"{self.name}: {self.effect}"


# Predefined spells
CANTRIPS = {
    "feu follet": Spell(
        name="Feu follet",
        school=SpellSchool.EVOCATION,
        level=0,
        casting_time="1 action",
        range="60 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 round",
        description="Vous créez une flamme dans votre main qui éclaire 10 pieds et inflige des dégâts.",
        effect="Lancez un jet d'attaque à distance contre une cible. En cas de toucher, la cible subit 1d10 dégâts de feu.",
        damage_dice="d10",
        damage_type="feu",
        attack_type="ranged"
    ),
    "rayon de givre": Spell(
        name="Rayon de givre",
        school=SpellSchool.EVOCATION,
        level=0,
        casting_time="1 action",
        range="60 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="Instantané",
        description="Un rayon de froid glacé jaillit de votre main.",
        effect="Lancez un jet d'attaque à distance contre une cible. En cas de toucher, la cible subit 1d8 dégâts de froid et sa vitesse est réduite de 3 mètres jusqu'au début de votre prochain tour.",
        damage_dice="d8",
        damage_type="froid",
        attack_type="ranged"
    ),
    "main du mage": Spell(
        name="Main du mage",
        school=SpellSchool.CONJURATION,
        level=0,
        casting_time="1 action",
        range="30 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 minute",
        description="Une main spectrale apparaît et effectue une tâche simple.",
        effect="La main peut manipuler un objet, ouvrir une porte non verrouillée, ou tenir un objet. Elle peut aussi lancer un objet jusqu'à 15 pieds. La main disparaît si elle s'éloigne de plus de 30 pieds de vous."
    ),
    "prestidigitations": Spell(
        name="Prestidigitations",
        school=SpellSchool.TRANSMUTATION,
        level=0,
        casting_time="1 action",
        range="10 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 heure",
        description="Tour de magie mineur pour impressionner ou distraire.",
        effect="Vous créez un effet sensoriel inoffensif, comme des étincelles, un léger vent, ou un son faible. Vous pouvez aussi nettoyer ou salir un objet, réchauffer ou refroidir un petit objet, ou créer une petite marque ou un symbole."
    ),
    "lueurs féeriques": Spell(
        name="Lueurs féeriques",
        school=SpellSchool.EVOCATION,
        level=0,
        casting_time="1 action",
        range="60 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 minute",
        description="Des lumières colorées dansent autour de vos doigts.",
        effect="Vous créez des lumières colorées qui peuvent éclairer 10 pieds ou aveugler une créature pendant 1 round (jet de sauvegarde de Dextérité)."
    ),
}

LEVEL_1_SPELLS = {
    "bouclier": Spell(
        name="Bouclier",
        school=SpellSchool.ABJURATION,
        level=1,
        casting_time="1 action bonus",
        range="Soit-même",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 round",
        description="Un champ de force magique apparaît et vous protège.",
        effect="Jusqu'au début de votre prochain tour, vous gagnez +5 à votre CA, y compris contre les sorts déjà lancés, et vous êtes immunisé contre les dégâts de magie.",
        concentration=True
    ),
    "projectile magique": Spell(
        name="Projectile magique",
        school=SpellSchool.EVOCATION,
        level=1,
        casting_time="1 action",
        range="120 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="Instantané",
        description="Vous créez un projectile magique qui frappe infailliblement sa cible.",
        effect="Vous lancez un projectile qui touche automatiquement sa cible. Le projectile inflige 1d4+1 dégâts de force. Les projectiles supplémentaires (1 par 2 niveaux au-delà du 1er) infligent chacun 1d4+1 dégâts.",
        damage_dice="d4",
        damage_type="force"
    ),
    "cure légère": Spell(
        name="Cure légère",
        school=SpellSchool.EVOCATION,
        level=1,
        casting_time="1 action",
        range="Toucher",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="Instantané",
        description="Un flux de pouvoir guérisseur passe à travers la créature touchée.",
        effect="La cible récupère 1d8 points de vie + 1 par niveau de sort (max +5)."
    ),
    "charme-personne": Spell(
        name="Charme-personne",
        school=SpellSchool.ENCHANTMENT,
        level=1,
        casting_time="1 action",
        range="30 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 heure",
        description="Vous tentez de charmer une créature humaine.",
        effect="La cible doit réussir un jet de sauvegarde de Sagesse ou être charmée par vous. Si la cible ou ses alliés vous attaquent, le sort se termine.",
        save="WIS"
    ),
    "détection de la magie": Spell(
        name="Détection de la magie",
        school=SpellSchool.DIVINATION,
        level=1,
        casting_time="1 action",
        range="Soit-même",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="Concentration, jusqu'à 10 minutes",
        description="Vous détectez la présence de magie dans un rayon de 30 pieds.",
        effect="Pendant la durée, vous sentez la présence de magie dans un rayon de 30 pieds. Vous pouvez utiliser une action pour voir une aura autour de chaque objet ou créature magique.",
        concentration=True,
        ritual=True
    ),
    "saut": Spell(
        name="Saut",
        school=SpellSchool.TRANSMUTATION,
        level=1,
        casting_time="1 action",
        range="Toucher",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 minute",
        description="La créature touchée voit sa capacité de saut tripler.",
        effect="La cible peut sauter trois fois plus loin que normalement. Le sort se termine si la cible utilise cette capacité pour attaquer."
    ),
    "peau d'écorce": Spell(
        name="Peau d'écorce",
        school=SpellSchool.TRANSMUTATION,
        level=1,
        casting_time="1 action",
        range="Toucher",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="Concentration, jusqu'à 1 heure",
        description="La peau de la cible devient aussi dure que l'écorce.",
        effect="La CA de la cible devient 16 (ou 13 + son modificateur de Dextérité, selon ce qui est le plus élevé).",
        concentration=True
    ),
}

LEVEL_2_SPELLS = {
    "boule de feu": Spell(
        name="Boule de feu",
        school=SpellSchool.EVOCATION,
        level=2,
        casting_time="1 action",
        range="150 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC, SpellComponent.MATERIAL],
        duration="Instantané",
        description="Une boule de feu explose à un endroit de votre choix.",
        effect="Chaque créature dans un rayon de 6 mètres doit réussir un jet de sauvegarde de Dextérité ou subir 8d6 dégâts de feu (la moitié en cas de réussite).",
        damage_dice="8d6",
        damage_type="feu",
        save="DEX"
    ),
    "invisibilité": Spell(
        name="Invisibilité",
        school=SpellSchool.ILLUSION,
        level=2,
        casting_time="1 action",
        range="Toucher",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC, SpellComponent.MATERIAL],
        duration="Concentration, jusqu'à 1 heure",
        description="La créature touchée devient invisible.",
        effect="La cible est invisible jusqu'à ce qu'elle attaque ou lance un sort, ou jusqu'à la fin du sort.",
        concentration=True
    ),
    "miroir mental": Spell(
        name="Miroir mental",
        school=SpellSchool.ABJURATION,
        level=2,
        casting_time="1 action bonus",
        range="Soit-même",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="1 minute",
        description="Vous protégez votre esprit contre les intrusions.",
        effect="Vous gagnez une résistance aux dégâts psychiques. De plus, si une créature tente de lire vos pensées, de vous charmer, ou de vous posséder, elle doit réussir un jet de sauvegarde de Charisme ou échouer.",
        concentration=True
    ),
    "soins": Spell(
        name="Soins",
        school=SpellSchool.EVOCATION,
        level=2,
        casting_time="1 action",
        range="60 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC],
        duration="Instantané",
        description="Un flux de pouvoir guérisseur passe à travers les créatures de votre choix.",
        effect="Jusqu'à 3 créatures de votre choix récupèrent 2d8 + votre modificateur de lanceur de sorts points de vie."
    ),
    "flèche acide": Spell(
        name="Flèche acide",
        school=SpellSchool.EVOCATION,
        level=2,
        casting_time="1 action",
        range="90 pieds",
        components=[SpellComponent.VERBAL, SpellComponent.SOMATIC, SpellComponent.MATERIAL],
        duration="Instantané",
        description="Vous lancez une flèche d'acide corrosif.",
        effect="Lancez un jet d'attaque à distance. En cas de toucher, la cible subit 4d4 dégâts d'acide au début de chacun de ses tours pendant 2 rounds (1 round si jet de sauvegarde de Constitution réussi).",
        damage_dice="4d4",
        damage_type="acide",
        save="CON"
    ),
}

# Combine all spells
ALL_SPELLS = {**CANTRIPS, **LEVEL_1_SPELLS, **LEVEL_2_SPELLS}


def get_spell_by_name(name: str) -> Optional[Spell]:
    """Get a spell by its name"""
    return ALL_SPELLS.get(name.lower())


def get_spells_by_level(level: int) -> List[Spell]:
    """Get all spells of a specific level"""
    return [spell for spell in ALL_SPELLS.values() if spell.level == level]


def get_random_spell(level: Optional[int] = None) -> Spell:
    """Get a random spell"""
    import random
    
    if level is not None:
        spells = get_spells_by_level(level)
        if spells:
            return random.choice(spells)
    
    return random.choice(list(ALL_SPELLS.values()))


# Fix circular import
from .dice import roll_advantage, roll_disadvantage
