import os

# Configuration des raccourcis clavier
HOTKEY_CAPTURE_DOC = "ctrl+1"  # Numpad 1 usually maps to '1' depending on numlock, but 'ctrl+1' is safer generic
HOTKEY_CAPTURE_QUESTION = "ctrl+2"
HOTKEY_EXECUTE = "ctrl+3"
HOTKEY_CLEAR = "ctrl+0"

# Ghost-typing : la réponse IA est mise en mémoire et révélée caractère par caractère
# au fur et à mesure que l'utilisateur appuie sur des touches.
HOTKEY_GHOST_TOGGLE = "ctrl+decimal"  # Ctrl + Numpad .  (toggle ARMED / pause)
HOTKEY_GHOST_FLUSH  = "ctrl+num 5"    # Ctrl + Numpad 5  (colle le reste du buffer ; fallback : "ctrl+76")

# Configuration des modèles Gemini
# Ordre de priorité des modèles
MODELS = [
    "gemini-2.5-flash",        # Rapide et performant
    "gemini-2.5-flash-lite",   # Version légère en fallback
    "gemini-2.0-flash-exp",    # En dernier recours (si disponible)
]

# Instructions système
SYSTEM_INSTRUCTION = """
Tu es un assistant utile et direct.
Tes réponses doivent être concises, précises et dans un langage humain naturel et simple.
Ne fais pas de méta-commentaires (ex: "Voici la réponse", "J'ai compris").
Donne UNIQUEMENT la réponse à la question posée, point barre.
Si on te donne du contexte (Documents), utilise-le pour répondre.
"""
