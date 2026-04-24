import sys
import time
import msvcrt

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <seconds>", file=sys.stderr)
        sys.exit(1)
    
    duration = int(sys.argv[1])
    logged = []
    print(f"--- Inizio cattura per {duration} secondi ---")
    
    start = time.time()
    while time.time() - start < duration:
        if msvcrt.kbhit():
            # Legge il tasto premuto
            char = msvcrt.getch()
            
            # Gestione tasti speciali (frecce, F1-F12 ecc.)
            if char in (b'\x00', b'\xe0'):
                msvcrt.getch() # Consuma il secondo byte del tasto speciale
                continue
                
            try:
                decoded_char = char.decode('utf-8')
                logged.append(decoded_char)
                # Opzionale: mostra cosa stai scrivendo in tempo reale
                # sys.stdout.write(decoded_char)
                # sys.stdout.flush()
            except UnicodeDecodeError:
                pass
                
        time.sleep(0.01)
    
    print("\n--- Tempo scaduto. Output log: ---")
    output = ''.join(logged)
    print(output)
    sys.stdout.flush()

if __name__ == "__main__":
    main()
