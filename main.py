import keyboard
import pyperclip
import time
import winsound
import sys
from colorama import init, Fore, Style
from assistant import GeminiAssistant
import config

# Initialisation Colorama
init(autoreset=True)

def beep_confirm():
    try:
        winsound.Beep(440, 150) # Fréquence 440Hz, 150ms
    except:
        pass # Linux/Mac n'ont pas winsound, tant pis.

def beep_error():
    try:
        winsound.Beep(200, 300)
    except:
        pass

def get_selected_text():
    """Simule Ctrl+C pour récupérer la sélection active."""
    # Sauvegarde du contenu actuel du presse-papier
    old_clipboard = pyperclip.paste()
    
    # Nettoyage
    pyperclip.copy("") 
    
    # Simulation Copier
    keyboard.send("ctrl+c")
    time.sleep(0.1) # Laisser le temps à l'OS
    
    content = pyperclip.paste()
    
    if not content:
        # Si vide, on restaure l'ancien (optionnel, mais sympa)
        pyperclip.copy(old_clipboard)
        return None
        
    return content

def main():
    print(Fore.CYAN + "=== Gemini Desktop Assistant Initializing ===")
    
    try:
        assistant = GeminiAssistant()
        print(Fore.GREEN + "OK: Connexion API initialisée.")
    except Exception as e:
        print(Fore.RED + f"ERREUR INITIALISATION: {e}")
        print(Fore.YELLOW + "Vérifiez votre fichier .env")
        return

    print(f"""
{Fore.WHITE}Raccourcis actifs :
  {Fore.YELLOW}{config.HOTKEY_CAPTURE_DOC} {Fore.WHITE}: Ajouter la sélection aux Documents
  {Fore.YELLOW}{config.HOTKEY_CAPTURE_QUESTION} {Fore.WHITE}: Définir la sélection comme Question
  {Fore.YELLOW}{config.HOTKEY_EXECUTE} {Fore.WHITE}: Exécuter et coller la réponse
  {Fore.YELLOW}{config.HOTKEY_CLEAR} {Fore.WHITE}: Effacer le contexte
    """)
    print(Fore.CYAN + "L'assistant tourne en arrière-plan... (Ctrl+C dans ce terminal pour quitter)")

    # Callbacks pour les raccourcis
    
    def on_capture_doc():
        text = get_selected_text()
        if text:
            assistant.add_document(text)
            print(Fore.BLUE + f"[DOC] Ajouté ({len(text)} chars). Total docs: {len(assistant.documents)}")
            beep_confirm()
        else:
            print(Fore.RED + "[DOC] Aucun texte sélectionné détecté.")
            beep_error()

    def on_capture_question():
        text = get_selected_text()
        if text:
            assistant.set_question(text)
            print(Fore.MAGENTA + f"[QUESTION] Définie : {text[:50]}...")
            beep_confirm()
        else:
            print(Fore.RED + "[QUESTION] Aucun texte sélectionné détecté.")
            beep_error()

    def on_execute():
        print(Fore.YELLOW + "[EXEC] Génération en cours...")
        beep_confirm() # Petit bip de début
        
        response = assistant.generate_response()
        
        print(Fore.GREEN + "[EXEC] Réponse reçue. Collage...")
        pyperclip.copy(response)
        keyboard.send("ctrl+v")
        beep_confirm()

    def on_clear():
        assistant.clear_context()
        print(Fore.WHITE + "[CLEAR] Mémoire effacée.")
        beep_confirm()

    # Enregistrement des hotkeys
    # Note: keyboard.add_hotkey ne bloque pas, c'est parfait.
    keyboard.add_hotkey(config.HOTKEY_CAPTURE_DOC, on_capture_doc)
    keyboard.add_hotkey(config.HOTKEY_CAPTURE_QUESTION, on_capture_question)
    keyboard.add_hotkey(config.HOTKEY_EXECUTE, on_execute)
    keyboard.add_hotkey(config.HOTKEY_CLEAR, on_clear)

    # Boucle infinie pour garder le programme en vie
    keyboard.wait()

if __name__ == "__main__":
    main()
