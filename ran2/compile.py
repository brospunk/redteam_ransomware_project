# compile_ultra_simple.py
import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def compile_keep_only_exe(script_path):
    """Compila e mantiene SOLO il .exe, cancella tutto il resto"""
    
    script = Path(script_path)
    if not script.exists():
        print(f"❌ {script} non trovato")
        return False
    
    exe_name = script.stem
    
    print(f"🔧 Compilazione {script.name}...")
    
    try:
        # 1. Compila normalmente
        PyInstaller.__main__.run([
            str(script),
            '--onefile',
            '--console',
            '--clean',
            '--noconfirm',
            '--name', exe_name,
            '--hidden-import', 'cryptography',
            '--hidden-import', 'cryptography.fernet',
            '--hidden-import', 'requests',
        ])
        
        # 2. Sposta .exe dalla cartella dist/
        dist_exe = Path("dist") / f"{exe_name}.exe"
        current_exe = Path.cwd() / f"{exe_name}.exe"
        
        if dist_exe.exists():
            # Rinomina se esiste già
            counter = 1
            while current_exe.exists():
                current_exe = Path.cwd() / f"{exe_name}_{counter}.exe"
                counter += 1
            
            shutil.move(str(dist_exe), str(current_exe))
            
            # 3. PULIZIA TOTALE
            # Elimina dist/
            if Path("dist").exists():
                shutil.rmtree("dist")
            
            # Elimina build/
            if Path("build").exists():
                shutil.rmtree("build")
            
            # Elimina .spec
            spec_file = Path(f"{exe_name}.spec")
            if spec_file.exists():
                spec_file.unlink()
            
            print(f"✅ Creato: {current_exe.name}")
            print("🧹 Pulizia completata!")
            return True
        else:
            print("❌ .exe non creato")
            return False
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

# Uso:
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        compile_keep_only_exe(sys.argv[1])
    else:
        # Cerca automaticamente script .py
        for py_file in Path.cwd().glob("*.py"):
            if py_file.name != Path(__file__).name:  # Escludi questo script
                compile_keep_only_exe(py_file)
                break
        else:
            print("Nessun file .py trovato")
