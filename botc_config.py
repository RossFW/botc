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
