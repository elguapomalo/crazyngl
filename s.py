import sys
import time
from pynput import keyboard

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <seconds>", file=sys.stderr)
        sys.exit(1)

    duration = int(sys.argv[1])
    logged = []

    # Funzione chiamata ad ogni pressione di tasto
    def on_press(key):
        try:
            # Tasti alfanumerici
            logged.append(key.char)
        except AttributeError:
            # Tasti speciali (Space, Enter, etc.)
            if key == keyboard.Key.space:
                logged.append(" ")
            elif key == keyboard.Key.enter:
                logged.append("\n")
            else:
                logged.append(f"[{key}]")

    # Avvia il listener in background
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print(f"--- Monitoraggio globale attivo per {duration} secondi ---")
    time.sleep(duration)
    
    listener.stop()
    
    print("\n--- Log globale acquisito: ---")
    print(''.join(filter(None, logged)))

if __name__ == "__main__":
    main()
