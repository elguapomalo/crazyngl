import sys
import time
import msvcrt
import os

def main():
    # Se non viene passato il tempo, default a 10 secondi
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    # Percorso universale accessibile a tutti
    log_path = r"C:\Users\Public\global_log.txt"
    
    logged = []
    start = time.time()
    
    try:
        while time.time() - start < duration:
            if msvcrt.kbhit():
                # Legge il carattere senza attendere l'invio
                char = msvcrt.getch()
                try:
                    # Gestione caratteri speciali (Invio, Backspace, ecc.)
                    decoded_char = char.decode('utf-8')
                    if decoded_char == '\r':
                        logged.append('\n')
                    else:
                        logged.append(decoded_char)
                except:
                    # Per tasti non UTF-8 (F1, F2, Frecce)
                    logged.append(f"[{str(char)}]")
            time.sleep(0.01)
    except Exception as e:
        # In caso di errore, lo scriviamo comunque nel log
        with open(log_path, "a") as f:
            f.write(f"\nErrore durante l'esecuzione: {e}\n")

    # Scrittura finale sul file in modalità "append" per non sovrascrivere test precedenti
    with open(log_path, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n--- Sessione del {timestamp} ---\n")
        f.write(''.join(logged))
        f.write("\n--- Fine Sessione ---\n")

if __name__ == "__main__":
    main()
