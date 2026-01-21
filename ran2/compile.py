# compile_clean.py - VERSIONE CORRETTA
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

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
        # Usa python -m pip invece di pip direttamente
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"],
            capture_output=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        print("✅ PyInstaller installato/aggiornato")
    except subprocess.CalledProcessError:
        print("⚠️  PyInstaller già installato o errore nell'installazione")
    except Exception as e:
        print(f"⚠️  Nota: {e}")
    
    # 2. Crea una cartella temporanea per la compilazione
    print("\n2. Preparazione ambiente temporaneo...")
    temp_dir = tempfile.mkdtemp(prefix="pyinstaller_temp_")
    print(f"   Cartella temporanea: {temp_dir}")
    
    try:
        # 3. Compila nella cartella temporanea
        print("\n3. Compilazione in corso...")
        
        # Costruisci il comando PyInstaller usando python -m pyinstaller
        cmd = [
            sys.executable,  # Usa l'eseguibile Python corrente
            "-m",           # Esegui come modulo
            "pyinstaller",  # Modulo PyInstaller
            "--onefile",
            "--distpath", temp_dir,      # Output .exe nella temp
            "--workpath", os.path.join(temp_dir, "build"),  # Build nella temp
            "--specpath", temp_dir,      # Spec file nella temp
            "--clean",      # Pulisci cache precedente
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
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        if result.returncode != 0:
            print(f"❌ Errore nella compilazione (codice: {result.returncode}):")
            if result.stdout:
                print("Output stdout:", result.stdout[:500])
            if result.stderr:
                print("Output stderr:", result.stderr[:500])
            return False
        
        print("✅ Compilazione completata")
        
        # 4. Trova il .exe generato
        exe_temp_path = Path(temp_dir) / f"{script_name}.exe"
        
        if not exe_temp_path.exists():
            # Cerca qualsiasi .exe nella cartella temp
            exe_files = list(Path(temp_dir).glob("*.exe"))
            if exe_files:
                exe_temp_path = exe_files[0]
                print(f"Trovato .exe: {exe_temp_path.name}")
            else:
                # Prova anche in sottocartelle
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.exe'):
                            exe_temp_path = Path(root) / file
                            print(f"Trovato .exe in sottocartella: {exe_temp_path}")
                            break
                    if exe_temp_path.exists():
                        break
                
                if not exe_temp_path.exists():
                    print(f"❌ Nessun .exe trovato in {temp_dir}")
                    # Mostra cosa c'è nella cartella
                    print("Contenuto della cartella temporanea:")
                    for item in Path(temp_dir).iterdir():
                        print(f"  - {item.name}")
                    return False
        
        # 5. Sposta il .exe nella cartella dello script
        print("\n4. Spostamento .exe nella cartella originale...")
        exe_final_path = script_dir / exe_temp_path.name
        
        # Se esiste già, rinomina
        counter = 1
        original_name = exe_final_path.stem
        while exe_final_path.exists():
            new_name = f"{original_name}_{counter}.exe"
            exe_final_path = script_dir / new_name
            counter += 1
        
        try:
            shutil.move(str(exe_temp_path), str(exe_final_path))
            print(f"✅ .exe spostato in: {exe_final_path}")
        except Exception as e:
            print(f"❌ Errore durante lo spostamento: {e}")
            # Prova a copiare invece di spostare
            try:
                shutil.copy2(str(exe_temp_path), str(exe_final_path))
                print(f"✅ .exe copiato in: {exe_final_path}")
            except Exception as e2:
                print(f"❌ Errore anche nella copia: {e2}")
                return False
        
        # 6. Mostra informazioni sul file
        if exe_final_path.exists():
            size_bytes = exe_final_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            print(f"📏 Dimensione: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        else:
            print("⚠️  Attenzione: .exe non trovato nella destinazione finale")
        
        # 7. Pulisci la cartella temporanea
        print("\n5. Pulizia file temporanei...")
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("✅ File temporanei eliminati")
        except Exception as e:
            print(f"⚠️  Impossibile eliminare completamente i file temporanei: {e}")
        
        print("\n" + "=" * 60)
        print("✅ COMPILAZIONE PULITA COMPLETATA!")
        print(f"📁 Il tuo .exe è qui: {exe_final_path}")
        print("🧹 Nessun'altro file è stato creato!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la compilazione: {e}")
        import traceback
        traceback.print_exc()  # Mostra traceback completo
        
        # Pulisci comunque la temp
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("🧹 Cartella temporanea pulita")
        except:
            pass
        return False

def compile_current_folder():
    """Compila tutti gli script .py nella cartella corrente"""
    
    current_dir = Path.cwd()
    py_files = list(current_dir.glob("*.py"))
    
    # Rimuovi questo script stesso dalla lista
    this_script = Path(__file__).name
    py_files = [f for f in py_files if f.name != this_script]
    
    if not py_files:
        print("❌ Nessun file .py trovato nella cartella corrente.")
        return False
    
    print(f"📁 Cartella: {current_dir}")
    print(f"📄 Trovati {len(py_files)} file .py")
    
    success_count = 0
    for i, py_file in enumerate(py_files, 1):
        print(f"\n[{i}/{len(py_files)}] Compilazione: {py_file.name}")
        if compile_to_exe_clean(py_file):
            success_count += 1
    
    print(f"\n{'='*40}")
    print(f"RIEPILOGO: {success_count}/{len(py_files)} file compilati con successo")
    print(f"{'='*40}")
    
    return success_count > 0

def main():
    """Menu principale"""
    
    print("COMPILATORE PULITO PYTHON → .EXE")
    print("-" * 40)
    print("Questo script compila .py in .exe mantenendo SOLO il file .exe")
    print("Nessuna cartella build/, dist/ o file .spec sarà lasciato")
    print("-" * 40)
    
    if len(sys.argv) > 1:
        # Compila il file specificato
        for script in sys.argv[1:]:
            print(f"\nCompilazione di: {script}")
            compile_to_exe_clean(script)
    else:
        # Modalità interattiva
        print("\nOpzioni:")
        print("1. Compila un file .py specifico")
        print("2. Compila tutti i .py in questa cartella")
        print("3. Esci")
        
        try:
            choice = input("\nScelta (1-3): ").strip()
            
            if choice == "1":
                py_files = list(Path.cwd().glob("*.py"))
                this_script = Path(__file__).name
                py_files = [f for f in py_files if f.name != this_script]
                
                if py_files:
                    print("\nFile .py disponibili:")
                    for i, f in enumerate(py_files, 1):
                        print(f"{i}. {f.name}")
                    
                    try:
                        file_num = int(input("\nNumero del file da compilare: "))
                        if 1 <= file_num <= len(py_files):
                            compile_to_exe_clean(py_files[file_num - 1])
                        else:
                            print("❌ Numero non valido")
                    except ValueError:
                        print("❌ Inserisci un numero valido")
                else:
                    print("❌ Nessun file .py trovato (escluso questo script)")
                    
            elif choice == "2":
                compile_current_folder()
                
            elif choice == "3":
                print("Arrivederci!")
                return
                
            else:
                print("❌ Scelta non valida")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Operazione interrotta dall'utente")
        except Exception as e:
            print(f"❌ Errore: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Verifica se Python è disponibile
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Script interrotto")
    except Exception as e:
        print(f"❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPremi Invio per uscire...")
