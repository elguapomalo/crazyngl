import ctypes
from ctypes import wintypes
import time

# Caricamento librerie di sistema
user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Definizioni costanti Windows
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100

def low_level_handler(nCode, wParam, lParam):
    if nCode >= 0 and wParam == WM_KEYDOWN:
        vk_code = lParam.contents.vkCode
        # Stampa il codice virtuale del tasto
        print(f"Tasto intercettato (VK): {vk_code}")
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

# Struttura dati per il tasto
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

# Registrazione dell'hook
CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))
pointer = CMPFUNC(low_level_handler)

hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, pointer, kernel32.GetModuleHandleW(None), 0)

if not hook:
    print("Impossibile installare l'hook, m'Lord.")
    exit(1)

print("Hook installato. In attesa di input globale...")

# Ciclo dei messaggi necessario per far funzionare l'hook
msg = wintypes.MSG()
while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
