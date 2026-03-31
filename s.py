#!/usr/bin/env python3
import sys
import tty
import termios
import time
import select

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <seconds>", file=sys.stderr)
        sys.exit(1)
    
    duration = int(sys.argv[1])
    logged = []
    old = termios.tcgetattr(sys.stdin)
    
    try:
        tty.setcbreak(sys.stdin.fileno())
        start = time.time()
        while time.time() - start < duration:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                logged.append(sys.stdin.read(1))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
    
    print(''.join(logged), end='')

if __name__ == "__main__":
    main()
