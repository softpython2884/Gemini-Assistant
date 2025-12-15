import google.generativeai as genai
from google.api_core import exceptions
import os
from dotenv import load_dotenv
import config
import time

class GeminiAssistant:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erreur: Clé API non trouvée dans le fichier .env")
        
        genai.configure(api_key=api_key)
        
        self.documents = []
        self.current_question = ""
        
    def add_document(self, text):
        """Ajoute du texte au contexte 'Documents'."""
        if text:
            self.documents.append(text)
            return True
        return False

    def set_question(self, text):
        """Définit la question actuelle."""
        if text:
            self.current_question = text
            return True
        return False

    def clear_context(self):
        """Vide la mémoire."""
        self.documents = []
        self.current_question = ""

    def generate_response(self):
        """Génère une réponse en utilisant la stratégie de fallback."""
        if not self.current_question and not self.documents:
            return "Aucun contenu sélectionné (ni question ni documents)."

        # Construction du prompt
        full_content = []
        if self.documents:
            full_content.append("DOCUMENTS DU CONTEXTE:")
            for i, doc in enumerate(self.documents):
                full_content.append(f"--- Doc {i+1} ---\n{doc}\n")
        
        if self.current_question:
            full_content.append(f"QUESTION DE L'UTILISATEUR:\n{self.current_question}")
        else:
             # Cas rare où on a juste des docs, on demande un résumé par défaut ?
             # Ou on attend une question. Le user a dit "selectione question, selection doc".
             # Si pas de question, le comportement par défaut n'est pas spécifié, on suppose qu'il faut une question.
             # Mais pour être robuste, si pas de question, on résume.
             full_content.append("INSTRUCTION: Résume ces documents.")

        user_message = "\n".join(full_content)

        # Tentative avec les différents modèles
        for model_name in config.MODELS:
            try:
                print(f"[IA] Tentative avec le modèle : {model_name}...")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=config.SYSTEM_INSTRUCTION
                )
                
                response = model.generate_content(user_message)
                return response.text
            
            except exceptions.ResourceExhausted:
                print(f"[IA] Quota dépassé pour {model_name}. Essai du suivant...")
                continue # Passe au modèle suivant
            except Exception as e:
                print(f"[Erreur] Problème avec {model_name}: {e}")
                # On pourrait continuer ou s'arrêter. Par sécurité on continue.
                continue
        
        return "Désolé, tous les modèles sont indisponibles ou le quota est épuisé."
