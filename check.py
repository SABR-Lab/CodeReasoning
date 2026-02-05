import sys
import platform
import subprocess
import shutil

def check_environment():
    """Environment check"""
    # 1. Basic System Info
    system = platform.system().lower()
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]}")
    
    # 2. Check Defects4J
    d4j_executable = "defects4j.bat" if system == "windows" else "defects4j"
    
    # Check if executable exists in PATH
    if shutil.which(d4j_executable):
        print(f"✅ Defects4J found in PATH ({d4j_executable})")
        
        # Optional: Run a real command to ensure it's initialized
        # 'info -p Lang' is the standard "smoke test" for Defects4J
        try:
            print("   Verifying execution...", end=" ", flush=True)
            result = subprocess.run(
                [d4j_executable, "info", "-p", "Lang"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print("OK")
                return True
            else:
                print("Failed")
                print(f"⚠️ Defects4J is installed but returned an error:\n{result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"\n❌ Error running Defects4J: {e}")
            return False
    else:
        print("❌ Defects4J command not found (not in PATH)")
        return False

if __name__ == "__main__":
    check_environment()