# ==============================================================
#   FAUX HORS-LIGNE - Gestionnaire d'icone reseau
#   Joue uniquement sur l'affichage de l'icone (nlasvc/netprofm)
#   La connexion internet reelle n'est jamais coupee.
# ==============================================================

# --- Verification Admin obligatoire ---
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host ""
    Write-Host "  ERREUR : Il faut lancer PowerShell en Administrateur !" -ForegroundColor Red
    Write-Host ""
    Start-Sleep -Seconds 4
    Exit
}

# --- Fonctions ---

function Show-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "   ______          _   _   _                 _      _                 " -ForegroundColor Cyan
    Write-Host "  |  ____|        | | | | | |               | |    (_)                " -ForegroundColor Cyan
    Write-Host "  | |__ __ _ _   _| |_| |_| | ___  _ __ ___  | |     _  __ _ _ __   ___ " -ForegroundColor Cyan
    Write-Host "  |  __/ _` | | | | __|  _  |/ _ \| '__/ __| | |    | |/ _` | '_ \ / _ \" -ForegroundColor Cyan
    Write-Host "  | | | (_| | |_| | |_| | | | (_) | |  \__ \ | |____| | (_| | | | |  __/" -ForegroundColor Cyan
    Write-Host "  |_|  \__,_|\__,_|\__\_| |_/\___/|_|  |___/ |______|_|\__, |_| |_|\___|" -ForegroundColor Cyan
    Write-Host "                                                        __/ |           " -ForegroundColor Cyan
    Write-Host "                                                       |___/            " -ForegroundColor Cyan
    Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
}

function Get-IconState {
    # On se base sur netprofm car nlasvc en depend
    $svc = Get-Service -Name netprofm -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -eq 'Running') { return 'NORMAL' } else { return 'HORS-LIGNE' }
}

function Enable-FauxHorsLigne {
    Write-Host ""
    Write-Host "  --- ACTIVATION DU FAUX HORS-LIGNE ---" -ForegroundColor Green
    Write-Host "  Neutralisation de l'icone..." -ForegroundColor Cyan

    # 1. On empeche Windows de relancer les services tout seul
    cmd.exe /c 'sc failure nlasvc   reset= 0 actions= ""' > $null
    cmd.exe /c 'sc failure netprofm reset= 0 actions= ""' > $null

    # 2. On tue les processus de force
    taskkill /F /FI "SERVICES eq nlasvc"   > $null 2>&1
    taskkill /F /FI "SERVICES eq netprofm" > $null 2>&1

    Start-Sleep -Seconds 1
    Write-Host ""
    Write-Host "  C'est fait ! Le globe a du apparaitre." -ForegroundColor Green
}

function Restore-Normal {
    Write-Host ""
    Write-Host "  --- RETOUR A LA NORMALE ---" -ForegroundColor Yellow
    Write-Host "  Reveil de la barre des taches..." -ForegroundColor Cyan

    # 1. On remet la recuperation automatique par defaut sur les 2 services
    cmd.exe /c 'sc failure nlasvc   reset= 86400 actions= restart/60000/restart/60000/restart/60000' > $null
    cmd.exe /c 'sc failure netprofm reset= 86400 actions= restart/60000/restart/60000/restart/60000' > $null

    # 2. On remet les bons types de demarrage
    Set-Service -Name netprofm -StartupType Manual    -ErrorAction SilentlyContinue
    Set-Service -Name nlasvc   -StartupType Automatic  -ErrorAction SilentlyContinue

    # 3. ORDRE IMPORTANT : netprofm AVANT nlasvc (nlasvc en depend)
    $ok = $true
    try   { Start-Service -Name netprofm -ErrorAction Stop }
    catch { $ok = $false; Write-Host "  Echec netprofm : $($_.Exception.Message)" -ForegroundColor Red }

    try   { Start-Service -Name nlasvc -ErrorAction Stop }
    catch { $ok = $false; Write-Host "  Echec nlasvc : $($_.Exception.Message)" -ForegroundColor Red }

    Start-Sleep -Seconds 1
    Write-Host ""
    if ($ok) {
        Write-Host "  C'est fait ! La vraie icone Wi-Fi est de retour." -ForegroundColor Green
    } else {
        Write-Host "  Probleme : redemarre le PC, les services reviennent au boot." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "  Etat des services :" -ForegroundColor DarkGray
    Get-Service nlasvc, netprofm | Format-Table Name, Status, StartType -AutoSize
}

function Force-Redetection {
    Write-Host ""
    Write-Host "  --- FORCER LA RE-DETECTION INTERNET ---" -ForegroundColor Magenta

    # 1. On s'assure que les 2 services tournent (ordre important)
    Write-Host "  Verification des services..." -ForegroundColor Cyan
    try { Start-Service -Name netprofm -ErrorAction Stop } catch {}
    try { Start-Service -Name nlasvc   -ErrorAction Stop } catch {}

    # 2. On redemarre la/les carte(s) reseau actives -> NLA refait son test
    Write-Host "  Redemarrage de la carte reseau (coupure ~5s)..." -ForegroundColor Cyan
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
    if ($adapters) {
        foreach ($a in $adapters) {
            try {
                Restart-NetAdapter -Name $a.Name -ErrorAction Stop
                Write-Host "    -> $($a.Name) redemarree" -ForegroundColor DarkGray
            } catch {
                # Plan B si Restart echoue : disable puis enable
                Disable-NetAdapter -Name $a.Name -Confirm:$false -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                Enable-NetAdapter  -Name $a.Name -Confirm:$false -ErrorAction SilentlyContinue
                Write-Host "    -> $($a.Name) reactivee (plan B)" -ForegroundColor DarkGray
            }
        }
    } else {
        Write-Host "    Aucune carte active detectee." -ForegroundColor Yellow
    }

    # 3. On vide le cache DNS au passage
    Write-Host "  Nettoyage du cache DNS..." -ForegroundColor Cyan
    ipconfig /flushdns > $null

    # 4. On laisse le temps a la carte de remonter et a NLA de re-tester
    Write-Host "  Attente de la reconnexion..." -ForegroundColor Cyan
    Start-Sleep -Seconds 6

    Write-Host ""
    Write-Host "  Termine ! L'icone devrait afficher l'acces internet." -ForegroundColor Green
    Write-Host "  (Si ce n'est pas le cas, deconnecte/reconnecte le Wi-Fi" -ForegroundColor DarkGray
    Write-Host "   ou redemarre le PC : NLA re-teste tout au boot.)" -ForegroundColor DarkGray
}

# --- Boucle principale du menu ---

do {
    Show-Banner

    $etat = Get-IconState
    if ($etat -eq 'NORMAL') {
        Write-Host "  Etat actuel : " -NoNewline; Write-Host "ICONE NORMALE (services actifs)" -ForegroundColor Green
    } else {
        Write-Host "  Etat actuel : " -NoNewline; Write-Host "FAUX HORS-LIGNE (icone globe)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "  [1] " -ForegroundColor White -NoNewline; Write-Host "Activer le faux hors-ligne (afficher le globe)"
    Write-Host "  [2] " -ForegroundColor White -NoNewline; Write-Host "Revenir a la normale (vraie icone Wi-Fi)"
    Write-Host "  [4] " -ForegroundColor White -NoNewline; Write-Host "Forcer la re-detection internet (corrige 'pas d'internet')"
    Write-Host "  [3] " -ForegroundColor White -NoNewline; Write-Host "Quitter"
    Write-Host ""
    $choix = Read-Host "  Ton choix"

    switch ($choix) {
        '1' { Enable-FauxHorsLigne; Write-Host ""; Read-Host "  Appuie sur Entree pour revenir au menu" }
        '2' { Restore-Normal;       Write-Host ""; Read-Host "  Appuie sur Entree pour revenir au menu" }
        '4' { Force-Redetection;    Write-Host ""; Read-Host "  Appuie sur Entree pour revenir au menu" }
        '3' { Write-Host ""; Write-Host "  A plus !" -ForegroundColor Cyan; Start-Sleep -Seconds 1 }
        default {
            Write-Host ""
            Write-Host "  Choix invalide, tape 1, 2, 4 ou 3." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }

} while ($choix -ne '3')