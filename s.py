import sys
import time
import msvcrt # Libreria specifica per Windows per catturare i tasti

def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    
    duration = int(sys.argv[1])
    logged = []
    
    start = time.time()
    # Ciclo di cattura
    while time.time() - start < duration:
        if msvcrt.kbhit(): # Controlla se un tasto è stato premuto
            char = msvcrt.getch() # Legge il tasto (restituisce bytes)
            # Decodifica il carattere e lo aggiunge alla lista
            try:
                logged.append(char.decode('utf-8'))
            except:
                logged.append(str(char))
        time.sleep(0.01) # Riduce il carico sulla CPU
    
    # Scrittura su file
    with open("C:\\Python311\\test.txt", "w") as f:
        f.write(''.join(logged))

if __name__ == "__main__":
    main()
