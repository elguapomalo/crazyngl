import sys
import pywintypes
import win32ts
import win32security
import win32process
import win32con
import win32api
import win32profile

def enable_privilege(priv_name: str):
    hToken = win32security.OpenProcessToken(
        win32api.GetCurrentProcess(),
        win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    )
    priv_id = win32security.LookupPrivilegeValue(None, priv_name)
    win32security.AdjustTokenPrivileges(
        hToken,
        False,
        [(priv_id, win32security.SE_PRIVILEGE_ENABLED)]
    )

def run_in_user_session(command: str):
    enable_privilege("SeAssignPrimaryTokenPrivilege")
    enable_privilege("SeIncreaseQuotaPrivilege")
    enable_privilege("SeTcbPrivilege")

    session_id = win32ts.WTSGetActiveConsoleSessionId()
    if session_id == 0xFFFFFFFF:
        raise RuntimeError("No active console session found")

    user_token = win32ts.WTSQueryUserToken(session_id)

    sa = pywintypes.SECURITY_ATTRIBUTES()
    sa.bInheritHandle = False

    primary_token = win32security.DuplicateTokenEx(
        user_token,
        win32con.MAXIMUM_ALLOWED,
        sa,
        win32security.SecurityImpersonation,
        win32security.TokenPrimary
    )

    env = win32profile.CreateEnvironmentBlock(primary_token, False)

    startup = win32process.STARTUPINFO()
    startup.dwFlags = win32con.STARTF_USESHOWWINDOW
    startup.wShowWindow = win32con.SW_SHOW
    startup.lpDesktop = "winsta0\\default"

    proc_info = win32process.CreateProcessAsUser(
        primary_token,
        None,
        command,
        None,
        None,
        False,
        win32con.CREATE_NEW_CONSOLE,
        env,
        None,
        startup
    )

    user_token.Close()
    primary_token.Close()

    return proc_info

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python imp.py <command>")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    hProcess, hThread, pid, tid = run_in_user_session(command)
    print(f"Launched PID {pid}: {command}")
