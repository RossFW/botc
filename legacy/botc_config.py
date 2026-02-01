"""
Centralized configuration for Blood on the Clocktower (BOTC) analytics.

This module contains script categorization and lists that are used across
all analytics and ELO tracking scripts. Update this file to add new scripts
or change categorization, and all dependent scripts will automatically use
the updated values.
"""

# Scripts considered part of the normal rotation. All other scripts are
# considered Teensyville (small‑player) scripts.
NORMAL_SCRIPTS = {
    "trouble brewing",
    "bad moon rising",
    "sects & violets",
    "trouble in violets",
    "trouble in legion",
    "hide & seek",
    "trouble brewing on expert mode",
    "trained killer",
    "irrational behavior",
    "binary supernovae",
    "everybody can play"
}

# List of commonly used game modes/scripts for dropdown menus.
# This is a convenience list - users can still type custom script names.
# Note: These should match the capitalization used in the game log for consistency.
COMMON_SCRIPTS = [
    "Trouble Brewing",
    "Bad Moon Rising",
    "Sects & Violets",
    "Trouble in Violets",
    "No Greater Joy",
    "Over the River",
    "Laissez un Faire",
    "Trouble in Legion",
    "Hide & Seek",
    "Trouble Brewing on Expert Mode",
    "Trained Killer",
    "Irrational Behavior",
    "Binary Supernovae",
    "A Leech of Distrust",
    "Everybody Can Play",
]


def normalize_script_name(name: str) -> str:
    """Return a lowercase stripped version of a script name for comparison."""
    return (name or "").strip().lower()


def categorize_script(name: str) -> str:
    """
    Categorize a script as 'Normal' or 'Teensyville'.
    
    Parameters
    ----------
    name : str
        The script name to categorize.
    
    Returns
    -------
    str
        Either "Normal" if the script is in NORMAL_SCRIPTS, else "Teensyville".
    """
    return "Normal" if normalize_script_name(name) in NORMAL_SCRIPTS else "Teensyville"


# Mapping of normalized character names to their role types.
# Character names are normalized (spaces -> underscores, lowercase)
# to handle both CSV format (spaces) and game log format (underscores).
CHARACTER_ROLE_TYPES = {
    # Demons
    "al-hadikhia": "Demons",
    "fang_gu": "Demons",
    "imp": "Demons",
    "kazali": "Demons",
    "legion": "Demons",
    "leviathan": "Demons",
    "lil'_monsta": "Demons",
    "lleech": "Demons",
    "lord_of_typhon": "Demons",
    "no_dashii": "Demons",  # CSV spelling
    "no_dashi": "Demons",  # Game log spelling (one 'i')
    "ojo": "Demons",
    "po": "Demons",
    "pukka": "Demons",
    "riot": "Demons",
    "shabaloth": "Demons",
    "vigormortis": "Demons",
    "vortox": "Demons",
    "yaggababble": "Demons",
    "zombuul": "Demons",
    # Minions
    "assassin": "Minions",
    "baron": "Minions",
    "boffin": "Minions",
    "boomdandy": "Minions",
    "cerenovus": "Minions",
    "devil's_advocate": "Minions",
    "evil_twin": "Minions",
    "fearmonger": "Minions",
    "goblin": "Minions",
    "godfather": "Minions",
    "harpy": "Minions",
    "marionette": "Minions",
    "mastermind": "Minions",
    "mezepheles": "Minions",
    "organ_grinder": "Minions",
    "pit-hag": "Minions",
    "pithag": "Minions",  # Alternative spelling found in game log
    "poisoner": "Minions",
    "psychopath": "Minions",
    "scarlet_woman": "Minions",
    "spy": "Minions",
    "summoner": "Minions",
    "vizier": "Minions",
    "widow": "Minions",
    "witch": "Minions",
    "wizard": "Minions",
    "wraith": "Minions",
    "xaan": "Minions",
    # Outsiders
    "barber": "Outsiders",
    "butler": "Outsiders",
    "damsel": "Outsiders",
    "drunk": "Outsiders",
    "golem": "Outsiders",
    "goon": "Outsiders",
    "hatter": "Outsiders",
    "heretic": "Outsiders",
    "hermit": "Outsiders",
    "klutz": "Outsiders",
    "lunatic": "Outsiders",
    "moonchild": "Outsiders",
    "mutant": "Outsiders",
    "ogre": "Outsiders",
    "plague_doctor": "Outsiders",
    "politician": "Outsiders",
    "puzzlemaster": "Outsiders",
    "recluse": "Outsiders",
    "saint": "Outsiders",
    "snitch": "Outsiders",
    "sweetheart": "Outsiders",
    "tinker": "Outsiders",
    "zealot": "Outsiders",
    # Townsfolk
    "acrobat": "Townsfolk",
    "alchemist": "Townsfolk",
    "alsaahir": "Townsfolk",
    "amnesiac": "Townsfolk",
    "artist": "Townsfolk",
    "atheist": "Townsfolk",
    "balloonist": "Townsfolk",
    "banshee": "Townsfolk",
    "bounty_hunter": "Townsfolk",
    "cannibal": "Townsfolk",
    "chambermaid": "Townsfolk",
    "chef": "Townsfolk",
    "choirboy": "Townsfolk",
    "clockmaker": "Townsfolk",
    "courtier": "Townsfolk",
    "cult_leader": "Townsfolk",
    "dreamer": "Townsfolk",
    "empath": "Townsfolk",
    "engineer": "Townsfolk",
    "exorcist": "Townsfolk",
    "farmer": "Townsfolk",
    "fisherman": "Townsfolk",
    "flowergirl": "Townsfolk",
    "fool": "Townsfolk",
    "fortune_teller": "Townsfolk",
    "gambler": "Townsfolk",
    "general": "Townsfolk",
    "gossip": "Townsfolk",
    "grandmother": "Townsfolk",
    "high_priestess": "Townsfolk",
    "huntsman": "Townsfolk",
    "innkeeper": "Townsfolk",
    "investigator": "Townsfolk",
    "juggler": "Townsfolk",
    "king": "Townsfolk",
    "knight": "Townsfolk",
    "librarian": "Townsfolk",
    "lycanthrope": "Townsfolk",
    "magician": "Townsfolk",
    "mathematician": "Townsfolk",
    "mayor": "Townsfolk",
    "minstrel": "Townsfolk",
    "monk": "Townsfolk",
    "nightwatchman": "Townsfolk",
    "noble": "Townsfolk",
    "oracle": "Townsfolk",
    "pacifist": "Townsfolk",
    "philosopher": "Townsfolk",
    "pixie": "Townsfolk",
    "poppy_grower": "Townsfolk",
    "preacher": "Townsfolk",
    "princess": "Townsfolk",
    "professor": "Townsfolk",
    "ravenkeeper": "Townsfolk",
    "sage": "Townsfolk",
    "sailor": "Townsfolk",
    "savant": "Townsfolk",
    "seamstress": "Townsfolk",
    "shugenja": "Townsfolk",
    "slayer": "Townsfolk",
    "snake_charmer": "Townsfolk",
    "soldier": "Townsfolk",
    "steward": "Townsfolk",
    "tea_lady": "Townsfolk",
    "town_crier": "Townsfolk",
    "undertaker": "Townsfolk",
    "village_idiot": "Townsfolk",
    "virgin": "Townsfolk",
    "washerwoman": "Townsfolk",
    # Travellers
    "apprentice": "Travellers",
    "barista": "Travellers",
    "beggar": "Travellers",
    "bishop": "Travellers",
    "bone_collector": "Travellers",
    "bureaucrat": "Travellers",
    "butcher": "Travellers",
    "cacklejack": "Travellers",
    "deviant": "Travellers",
    "gangster": "Travellers",
    "gnome": "Travellers",
    "gunslinger": "Travellers",
    "harlot": "Travellers",
    "judge": "Travellers",
    "matron": "Travellers",
    "scapegoat": "Travellers",
    "thief": "Travellers",
    "voudon": "Travellers",
}


def normalize_character_name(name: str) -> str:
    """
    Normalize a character name for consistent lookups.
    
    Converts spaces to underscores, handles apostrophes and hyphens,
    and makes it lowercase for case-insensitive matching.
    
    This handles both CSV format (spaces) and game log format (underscores).
    
    Parameters
    ----------
    name : str
        The character name to normalize (e.g., "Fortune Teller" or "Fortune_Teller").
    
    Returns
    -------
    str
        Normalized name (e.g., "fortune_teller").
    
    Examples
    --------
    >>> normalize_character_name("Fortune Teller")
    'fortune_teller'
    >>> normalize_character_name("Devil's Advocate")
    "devil's_advocate"
    >>> normalize_character_name("Pit-Hag")
    'pit-hag'
    """
    if not name:
        return ""
    # Replace spaces with underscores, preserve apostrophes and hyphens
    normalized = name.replace(" ", "_").lower().strip()
    return normalized


def get_character_role_type(character_name: str) -> str:
    """
    Get the role type for a character.
    
    Parameters
    ----------
    character_name : str
        The character name (can be in any format: spaces, underscores, etc.).
    
    Returns
    -------
    str
        The role type: "Townsfolk", "Outsiders", "Minions", "Demons", or "Travellers".
    
    Raises
    ------
    KeyError
        If the character name is not found in CHARACTER_ROLE_TYPES.
        This indicates either a typo or a character not yet documented.
    
    Examples
    --------
    >>> get_character_role_type("Fortune Teller")
    'Townsfolk'
    >>> get_character_role_type("Imp")
    'Demons'
    """
    normalized = normalize_character_name(character_name)
    
    # Try exact match first
    if normalized in CHARACTER_ROLE_TYPES:
        return CHARACTER_ROLE_TYPES[normalized]
    
    # Try with hyphen replaced by underscore (for cases like "pit-hag" vs "pit_hag")
    if "-" in normalized:
        alt_normalized = normalized.replace("-", "_")
        if alt_normalized in CHARACTER_ROLE_TYPES:
            return CHARACTER_ROLE_TYPES[alt_normalized]
    
    # Try with underscore replaced by hyphen (reverse case)
    if "_" in normalized:
        alt_normalized = normalized.replace("_", "-")
        if alt_normalized in CHARACTER_ROLE_TYPES:
            return CHARACTER_ROLE_TYPES[alt_normalized]
    
    # Character not found
    raise KeyError(
        f"Character '{character_name}' (normalized: '{normalized}') not found in "
        f"CHARACTER_ROLE_TYPES. This may indicate a typo or a character that needs "
        f"to be added to botc_config.py."
    )
