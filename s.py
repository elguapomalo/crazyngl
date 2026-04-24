import sys
import time
import msvcrt

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <seconds>", file=sys.stderr)
        sys.exit(1)
    
    duration = int(sys.argv[1])
    logged = []
    start = time.time()

    while time.time() - start < duration:
        # Verifica se è stato premuto un tasto senza bloccare il ciclo
        if msvcrt.kbhit():
            char = msvcrt.getch().decode('utf-8', errors='ignore')
            logged.append(char)
        time.sleep(0.01) # Riduce il carico sulla CPU
    
    print(''.join(logged), end='')

if __name__ == "__main__":
    main()
