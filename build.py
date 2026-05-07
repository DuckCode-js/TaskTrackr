import subprocess
import sys
import os
import urllib.request
import time
import ctypes

os.chdir(os.path.dirname(os.path.abspath(__file__)))

ISCC_PATHS = [
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_iscc():
    for p in ISCC_PATHS:
        if os.path.exists(p):
            return p
    return None

def install_inno():
    if not is_admin():
        print("\nAdmin rights required to install Inno Setup.")
        print("Right-click build.bat and select 'Run as administrator', then try again.")
        return False
    print("Downloading Inno Setup...")
    url = "https://jrsoftware.org/download.php/is.exe"
    dest = os.path.join(os.environ.get('TEMP', '.'), 'innosetup.exe')
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:
        print(f"Download failed: {e}")
        print("Check your internet connection and try again.")
        return False
    print("Installing silently...")
    r = subprocess.run([dest, '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-'])
    time.sleep(4)
    return r.returncode == 0

def main():
    print("=== TaskTrackr Build ===\n")

    print("[1/2] Bundling app with PyInstaller...")
    r = subprocess.run([sys.executable, '-m', 'PyInstaller', 'tasktrackr.spec', '--clean', '--noconfirm'])
    if r.returncode != 0:
        print("\nERROR: PyInstaller failed. See output above.")
        return False
    print("Bundle complete.\n")

    print("[2/2] Building Windows installer...")
    iscc = find_iscc()
    if not iscc:
        if not install_inno():
            return False
        iscc = find_iscc()

    if not iscc:
        print("\nERROR: Inno Setup not found after install. Try installing manually:")
        print("  https://jrsoftware.org/isinfo.php")
        return False

    r = subprocess.run([iscc, 'installer.iss'])
    if r.returncode != 0:
        print("\nERROR: Installer compilation failed.")
        return False

    print("\n✓ Installer ready: dist\\TaskTrackr-Setup.exe")
    print("\n=== Done ===")
    return True

if __name__ == '__main__':
    ok = main()
    if not ok:
        sys.exit(1)
