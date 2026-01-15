from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import config

class GeminiAssistant:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erreur: Clé API non trouvée dans le fichier .env")
        
        self.client = genai.Client(api_key=api_key)
        
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
             # Si pas de question, on résume.
             full_content.append("INSTRUCTION: Résume ces documents.")

        user_message = "\n".join(full_content)

        # Tentative avec les différents modèles
        for model_name in config.MODELS:
            try:
                print(f"[IA] Tentative avec le modèle : {model_name}...")
                
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=config.SYSTEM_INSTRUCTION
                    )
                )
                return response.text
            
            except Exception as e:
                # Note: google-genai might raise specific errors, keeping generic for now or checking string
                # If resource exhausted, usually it's a ClientError with 429
                error_str = str(e)
                if "429" in error_str or "ResourceExhausted" in error_str:
                     print(f"[IA] Quota dépassé pour {model_name}. Essai du suivant...")
                     continue
                
                print(f"[Erreur] Problème avec {model_name}: {e}")
                continue
        
        return "Désolé, tous les modèles sont indisponibles ou le quota est épuisé."
