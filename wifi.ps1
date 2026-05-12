# Verification Admin obligatoire
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERREUR : Il faut lancer PowerShell en Administrateur !" -ForegroundColor Red
    Start-Sleep -Seconds 3
    Exit
}

# On verifie si le service qui dessine l'icone est en cours
$NlaStatus = (Get-Service -Name nlasvc).Status

if ($NlaStatus -eq 'Running') {
    Write-Host "--- ACTIVATION DU FAUX HORS-LIGNE ---" -ForegroundColor Green
    Write-Host "Neutralisation brutale de l'icone..." -ForegroundColor Cyan
    
    # 1. On empeche Windows de ressusciter le service tout seul
    cmd.exe /c 'sc failure nlasvc reset= 0 actions= ""' > $null
    
    # 2. On TUE le processus de force (Bypass total des blocages du Rectorat/Windows)
    taskkill /F /FI "SERVICES eq nlasvc" > $null 2>&1
    taskkill /F /FI "SERVICES eq netprofm" > $null 2>&1
    
    Write-Host "C'est fait ! Le Globe a du apparaitre instantanement."
} else {
    Write-Host "--- RETOUR A LA NORMALE ---" -ForegroundColor Yellow
    Write-Host "Reveil de la barre des taches..." -ForegroundColor Cyan
    
    # 1. On remet la protection de redemarrage automatique par defaut
    cmd.exe /c 'sc failure nlasvc reset= 86400 actions= restart/60000/restart/60000/restart/60000' > $null
    
    # 2. On rallume les services proprement
    Start-Service -Name nlasvc -ErrorAction SilentlyContinue
    Start-Service -Name netprofm -ErrorAction SilentlyContinue
    
    Write-Host "C'est fait ! La vraie icone Wi-Fi est de retour."
}

Write-Host "Fermeture dans 6 secondes..."
Start-Sleep -Seconds 6