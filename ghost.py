"""Ghost-typing : la réponse IA est gardée en mémoire et révélée caractère par
caractère au rythme des frappes utilisateur. Chaque touche imprimable que tape
l'utilisateur est interceptée et remplacée par le caractère suivant du buffer.
"""

import keyboard
import pyperclip


# Etats de la machine
INACTIVE = "INACTIVE"   # mode off
ARMED    = "ARMED"      # mode on, pas de buffer
TYPING   = "TYPING"     # mode on, buffer non vide, hook actif
PAUSED   = "PAUSED"     # mode on, buffer non vide, hook en pause


# Touches qui ne consomment pas de caractère du buffer (passent à travers).
PASSTHROUGH_KEYS = {
    "shift", "left shift", "right shift",
    "ctrl", "left ctrl", "right ctrl",
    "alt", "left alt", "right alt",
    "windows", "left windows", "right windows",
    "caps lock", "num lock", "scroll lock",
    "backspace", "delete", "enter", "tab", "esc",
    "left", "right", "up", "down",
    "home", "end", "page up", "page down", "insert",
    "print screen", "pause", "menu",
}
PASSTHROUGH_KEYS.update(f"f{i}" for i in range(1, 25))


class GhostTyper:
    def __init__(self):
        self.state = INACTIVE
        self.buffer = ""
        self._hook_handle = None

    # --- API publique ---

    def is_active(self) -> bool:
        """True si on doit router la réponse IA vers le buffer plutôt que coller."""
        return self.state != INACTIVE

    def toggle(self):
        """Ctrl+Numpad-. : transitions selon l'état courant."""
        if self.state == INACTIVE:
            self.state = ARMED
        elif self.state == ARMED:
            self.state = INACTIVE
            self.buffer = ""
        elif self.state == TYPING:
            self.state = PAUSED
            self._uninstall_hook()
        elif self.state == PAUSED:
            self.state = TYPING
            self._install_hook()

    def load(self, text: str):
        """Charge la réponse IA dans le buffer et passe en TYPING."""
        self.buffer = text or ""
        if not self.buffer:
            self.state = ARMED
            self._uninstall_hook()
            return
        self.state = TYPING
        self._install_hook()

    def flush(self):
        """Ctrl+Numpad-5 : colle le reste du buffer d'un coup, retour en ARMED."""
        if self.state in (TYPING, PAUSED) and self.buffer:
            remaining = self.buffer
            self.buffer = ""
            self._uninstall_hook()
            self.state = ARMED
            pyperclip.copy(remaining)
            keyboard.send("ctrl+v")

    def status_str(self) -> str:
        if self.state in (TYPING, PAUSED):
            return f"[{self.state}] {len(self.buffer)} chars restants"
        return f"[{self.state}]"

    # --- Interne ---

    def _install_hook(self):
        if self._hook_handle is None:
            self._hook_handle = keyboard.hook(self._on_key, suppress=True)

    def _uninstall_hook(self):
        if self._hook_handle is not None:
            try:
                keyboard.unhook(self._hook_handle)
            except (KeyError, ValueError):
                pass
            self._hook_handle = None

    def _on_key(self, event):
        # Laisser passer si on n'est pas en TYPING (sécurité ; ne devrait pas arriver
        # car le hook est désinstallé hors TYPING).
        if self.state != TYPING:
            return True

        # Seulement les key-down (sinon on consommerait 2x par frappe).
        if event.event_type != "down":
            return True

        # Si un modificateur est tenu (Ctrl/Alt/Win), c'est probablement un raccourci
        # de l'utilisateur (Ctrl+S, Ctrl+., etc.) → ne pas consommer.
        if (keyboard.is_pressed("ctrl")
                or keyboard.is_pressed("alt")
                or keyboard.is_pressed("windows")):
            return True

        # Touches non imprimables → laisser passer.
        name = (event.name or "").lower()
        if name in PASSTHROUGH_KEYS:
            return True

        # Consommer un caractère du buffer.
        if not self.buffer:
            # Sécurité : si on est ici sans buffer, on désarme.
            self.state = ARMED
            self._uninstall_hook()
            return True

        ch = self.buffer[0]
        self.buffer = self.buffer[1:]
        keyboard.write(ch)

        if not self.buffer:
            # Buffer vidé : on désinstalle et on repasse ARMED (mode reste ON).
            self.state = ARMED
            # Déprogrammer le hook en différé pour ne pas le retirer dans son propre callback.
            keyboard.call_later(self._uninstall_hook, delay=0)

        return False  # supprime la frappe originale
