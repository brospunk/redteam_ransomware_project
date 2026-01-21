# compile_clean.py
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import time

def compile_to_exe_clean(script_path, keep_console=False):
    """
    Compila uno script Python in .exe e mantiene SOLO il .exe nella stessa cartella.
    Cancella tutto il resto che PyInstaller crea.
    
    Args:
        script_path (str): Percorso dello script Python da compilare
        keep_console (bool): Se True, mantiene la console (no --noconsole)
    
    Returns:
        bool: True se successo, False altrimenti
    """
    
    script_path = Path(script_path)
    
    # Verifica che lo script esista
    if not script_path.exists():
        print(f"❌ Errore: {script_path} non trovato!")
        return False
    
    if script_path.suffix != '.py':
        print(f"❌ Errore: {script_path} non è un file .py!")
        return False
    
    # Cartella dello script (dove verrà messo il .exe)
    script_dir = script_path.parent
    script_name = script_path.stem  # Nome senza estensione
    
    print("=" * 60)
    print(f"COMPILAZIONE PULITA: {script_path.name}")
    print(f"Cartella destinazione: {script_dir}")
    print("=" * 60)
    
    # 1. Installa PyInstaller se non presente
    print("\n1. Verifica PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"],
                      capture_output=True, check=True)
        print("✅ PyInstaller pronto")
    except:
        print("⚠️  PyInstaller già installato o errore nell'installazione")
    
    # 2. Crea una cartella temporanea per la compilazione
    print("\n2. Preparazione ambiente temporaneo...")
    temp_dir = tempfile.mkdtemp(prefix="pyinstaller_temp_")
    print(f"   Cartella temporanea: {temp_dir}")
    
    try:
        # 3. Compila nella cartella temporanea
        print("\n3. Compilazione in corso...")
        
        # Costruisci il comando PyInstaller
        cmd = [
            "pyinstaller",
            "--onefile",
            "--distpath", temp_dir,      # Output .exe nella temp
            "--workpath", os.path.join(temp_dir, "build"),  # Build nella temp
            "--specpath", temp_dir,      # Spec file nella temp
        ]
        
        if not keep_console:
            cmd.append("--noconsole")
        
        cmd.append(str(script_path))
        
        print(f"   Comando: {' '.join(cmd)}")
        
        # Esegui PyInstaller
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"❌ Errore nella compilazione:")
            print(result.stderr[:500])
            return False
        
        print("✅ Compilazione completata")
        
        # 4. Trova il .exe generato
        exe_temp_path = Path(temp_dir) / f"{script_name}.exe"
        
        if not exe_temp_path.exists():
            # Cerca qualsiasi .exe nella cartella temp
            exe_files = list(Path(temp_dir).glob("*.exe"))
            if exe_files:
                exe_temp_path = exe_files[0]
            else:
                print(f"❌ Nessun .exe trovato in {temp_dir}")
                return False
        
        # 5. Sposta il .exe nella cartella dello script
        print("\n4. Spostamento .exe nella cartella originale...")
        exe_final_path = script_dir / exe_temp_path.name
        
        # Se esiste già, rinomina
        counter = 1
        while exe_final_path.exists():
            new_name = f"{script_name}_{counter}.exe"
            exe_final_path = script_dir / new_name
            counter += 1
        
        shutil.move(str(exe_temp_path), str(exe_final_path))
        print(f"✅ .exe spostato in: {exe_final_path}")
        
        # 6. Mostra informazioni sul file
        size_mb = exe_final_path.stat().st_size / (1024 * 1024)
        print(f"📏 Dimensione: {size_mb:.2f} MB")
        
        # 7. Pulisci la cartella temporanea
        print("\n5. Pulizia file temporanei...")
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("✅ File temporanei eliminati")
        except:
            print("⚠️  Impossibile eliminare completamente i file temporanei")
        
        print("\n" + "=" * 60)
        print("✅ COMPILAZIONE PULITA COMPLETATA!")
        print(f"📁 Il tuo .exe è qui: {exe_final_path}")
        print("🧹 Nessun'altro file è stato creato!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la compilazione: {e}")
        # Pulisci comunque la temp
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        return False

def compile_current_folder():
    """Compila tutti gli script .py nella cartella corrente"""
    
    current_dir = Path.cwd()
    py_files = list(current_dir.glob("*.py"))
    
    if not py_files:
        print("❌ Nessun file .py trovato nella cartella corrente.")
        return False
    
    print(f"📁 Cartella: {current_dir}")
    print(f"📄 Trovati {len(py_files)} file .py")
    
    for i, py_file in enumerate(py_files, 1):
        print(f"\n[{i}/{len(py_files)}] Compilazione: {py_file.name}")
        compile_to_exe_clean(py_file)
    
    return True

def main():
    """Menu principale"""
    
    if len(sys.argv) > 1:
        # Compila il file specificato
        for script in sys.argv[1:]:
            compile_to_exe_clean(script)
    else:
        # Modalità interattiva
        print("COMPILATORE PULITO PYTHON → .EXE")
        print("-" * 40)
        print("Questo script:")
        print("1. Compila il tuo .py in .exe")
        print("2. Mantiene SOLO il .exe nella stessa cartella")
        print("3. Cancella TUTTO il resto (build/, dist/, .spec)")
        print("-" * 40)
        
        print("\nOpzioni:")
        print("1. Compila un file specifico")
        print("2. Compila tutti i .py in questa cartella")
        print("3. Specifica percorso manuale")
        
        try:
            choice = input("\nScelta (1-3): ").strip()
            
            if choice == "1":
                py_files = list(Path.cwd().glob("*.py"))
                if py_files:
                    for i, f in enumerate(py_files, 1):
                        print(f"{i}. {f.name}")
                    
                    file_num = int(input("\nNumero del file da compilare: "))
                    if 1 <= file_num <= len(py_files):
                        compile_to_exe_clean(py_files[file_num - 1])
                    else:
                        print("❌ Numero non valido")
                else:
                    print("❌ Nessun file .py trovato")
                    
            elif choice == "2":
                compile_current_folder()
                
            elif choice == "3":
                file_path = input("Percorso completo del file .py: ").strip()
                compile_to_exe_clean(file_path)
                
            else:
                print("❌ Scelta non valida")
                
        except Exception as e:
            print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
