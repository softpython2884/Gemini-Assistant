"""Lanceur unique : s'auto-élève en admin, puis lance wifi.ps1 + main.py."""

import ctypes
import subprocess
import sys
from pathlib import Path


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin():
    """Relance ce même script via ShellExecuteW avec verbe 'runas' (popup UAC)."""
    params = " ".join(f'"{a}"' for a in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)


def main():
    if not is_admin():
        relaunch_as_admin()
        sys.exit(0)

    here = Path(__file__).resolve().parent

    # wifi.ps1 — fire-and-forget, le script se ferme tout seul après 6s.
    subprocess.Popen(
        ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(here / "wifi.ps1")],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    # main.py — bloquant, garde la console ouverte tant que l'assistant tourne.
    subprocess.run([sys.executable, str(here / "main.py")], check=False)


if __name__ == "__main__":
    main()
