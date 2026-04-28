import sys
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
    # Enable required privileges
    enable_privilege("SeTcbPrivilege")
    enable_privilege("SeAssignPrimaryTokenPrivilege")
    enable_privilege("SeIncreaseQuotaPrivilege")

    session_id = win32ts.WTSGetActiveConsoleSessionId()
    if session_id == 0xFFFFFFFF:
        raise RuntimeError("No active console session found")

    # Get user token
    user_token = win32ts.WTSQueryUserToken(session_id)

    # Duplicate into a primary token
    sa = win32security.SECURITY_ATTRIBUTES()
    primary_token = win32security.DuplicateTokenEx(
        user_token,
        win32con.MAXIMUM_ALLOWED,
        sa,
        win32security.SecurityImpersonation,
        win32security.TokenPrimary
    )

    # Create environment for the user
    env = win32profile.CreateEnvironmentBlock(primary_token, False)

    # Startup info
    startup = win32process.STARTUPINFO()
    startup.dwFlags = win32con.STARTF_USESHOWWINDOW
    startup.wShowWindow = win32con.SW_SHOW

    # Create process
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

    # Clean up handles we don't need
    user_token.Close()
    primary_token.Close()

    return proc_info  # (hProcess, hThread, pid, tid)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python imp.py <command>")
        sys.exit(1)

    # Build command safely
    command = " ".join(sys.argv[1:])

    hProcess, hThread, pid, tid = run_in_user_session(command)

    print(f"Launched PID {pid}: {command}")
