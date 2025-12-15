# Gemini Desktop Assistant

Un assistant personnel léger et invisible qui vit dans votre presse-papier. Sélectionnez du texte, posez des questions, et obtenez des réponses de l'IA Google Gemini directement dans n'importe quelle application (Word, IDE, Navigateur, etc.).

## Fonctionnalités

*   **Invisible** : Tourne en arrière-plan.
*   **Contextuel** : Peut lire plusieurs "documents" (morceaux de texte copiés) avant de répondre.
*   **Résilient** : Bascule automatiquement entre les modèles (`gemini-2.5-flash`, `lite`, etc.) si les quotas sont dépassés.
*   **Simple** : Réponses directes, sans blabla.

## Installation

1.  **Prérequis** : Python 3.x installé.
2.  **Cloner le projet** ou télécharger les fichiers.
3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configuration** :
    *   Renommez le fichier `.env.example` en `.env`.
    *   Ajoutez votre [clé API Google Gemini](https://aistudio.google.com/app/apikey) dans le fichier :
        ```env
        GOOGLE_API_KEY=votre_cle_ici
        ```

## Utilisation

Lancez le script :
```bash
python main.py
```

### Raccourcis Clavier (Défaut)

| Raccourci | Action | Description |
| :--- | :--- | :--- |
| **Ctrl + 1** | `Capture Document` | Ajoute le texte sélectionné à la mémoire de l'assistant. (Fait `Ctrl+C` pour vous). |
| **Ctrl + 2** | `Capture Question` | Définit le texte sélectionné comme la question à poser. |
| **Ctrl + 3** | `Exécuter` | Envoie le contexte + la question à Gemini et **colle** la réponse à la position du curseur. |
| **Ctrl + 0** | `Clear` | Oublie tout (vide les documents et la question en mémoire). |

### Exemple de Workflow

1.  Vous lisez un article sur le web. Vous sélectionnez un paragraphe intéressant -> **Ctrl + 1** (Bip de confirmation).
2.  Vous allez dans votre IDE, sur une erreur de code. Vous sélectionnez l'erreur -> **Ctrl + 1**.
3.  Vous tapez (ou sélectionnez) "Explique le lien entre ce texte et cette erreur" -> **Ctrl + 2**.
4.  Vous placez votre curseur là où vous voulez la réponse -> **Ctrl + 3**.
5.  L'assistant réfléchit (Bip d'attente) puis écrit la réponse tout seul.

## Personnalisation

Vous pouvez modifier les touches dans `config.py`.

## Contact

Créé pour être l'assistant de bureau ultime, par nightfury@nationquest.fr
