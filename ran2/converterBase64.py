import base64
import os
from pathlib import Path

def encode_file_to_base64(file_path):
    """Codifica un file in base64"""
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            encoded_content = base64.b64encode(file_content)
            return encoded_content.decode('utf-8')
    except FileNotFoundError:
        print(f"Errore: File '{file_path}' non trovato.")
        return None
    except Exception as e:
        print(f"Errore durante la codifica: {e}")
        return None

def decode_base64_to_file(encoded_string, output_path):
    """Decodifica una stringa base64 in un file"""
    try:
        decoded_content = base64.b64decode(encoded_string)
        with open(output_path, 'wb') as file:
            file.write(decoded_content)
        return True
    except Exception as e:
        print(f"Errore durante la decodifica: {e}")
        return False

def save_encoded_to_file(encoded_string, output_path):
    """Salva la stringa base64 codificata in un file di testo"""
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(encoded_string)
        return True
    except Exception as e:
        print(f"Errore durante il salvataggio: {e}")
        return False

def get_file_path():
    """Chiede all'utente di inserire il percorso del file"""
    while True:
        file_path = input("Inserisci il percorso del file: ").strip()
        
        # Rimuove eventuali virgolette dal percorso
        file_path = file_path.strip('"\'')
        
        if os.path.exists(file_path):
            return file_path
        else:
            print("File non trovato. Riprova.")
            print("Suggerimento: Puoi trascinare il file direttamente nella finestra del terminale.")

def main():
    print("=" * 50)
    print("CODEC BASE64")
    print("=" * 50)
    
    while True:
        print("\nScegli un'opzione:")
        print("1. Codifica un file in base64")
        print("2. Decodifica un file base64")
        print("3. Esci")
        
        choice = input("\nScelta (1/2/3): ").strip()
        
        if choice == '1':
            print("\n" + "-" * 30)
            print("CODIFICA FILE")
            print("-" * 30)
            
            # Ottieni il percorso del file da codificare
            file_path = get_file_path()
            file_name = os.path.basename(file_path)
            
            # Codifica il file
            print(f"\nCodifica del file: {file_name}")
            encoded_content = encode_file_to_base64(file_path)
            
            if encoded_content:
                print("✓ File codificato con successo!")
                
                # Chiedi all'utente cosa fare con il risultato
                print("\nCosa vuoi fare con il risultato?")
                print("1. Visualizzare sullo schermo")
                print("2. Salvare in un file")
                print("3. Entrambi")
                
                action = input("\nScelta (1/2/3): ").strip()
                
                if action in ['1', '3']:
                    print("\n" + "=" * 50)
                    print("CONTENUTO BASE64:")
                    print("=" * 50)
                    # Mostra solo i primi 500 caratteri per non sovraccaricare il terminale
                    if len(encoded_content) > 500:
                        print(encoded_content[:500] + "...")
                        print(f"\n(Visualizzati solo i primi 500 caratteri su {len(encoded_content)})")
                    else:
                        print(encoded_content)
                
                if action in ['2', '3']:
                    # Suggerisci un nome file di default
                    default_output = f"{file_name}.base64.txt"
                    output_path = input(f"\nInserisci il percorso per salvare (premi Invio per '{default_output}'): ").strip()
                    
                    if not output_path:
                        output_path = default_output
                    
                    if save_encoded_to_file(encoded_content, output_path):
                        print(f"✓ Contenuto base64 salvato in: {output_path}")
                        print(f"Dimensioni: {len(encoded_content)} caratteri")
        
        elif choice == '2':
            print("\n" + "-" * 30)
            print("DECODIFICA FILE")
            print("-" * 30)
            
            print("Puoi decodificare da:")
            print("1. Un file di testo contenente base64")
            print("2. Incollare direttamente la stringa base64")
            
            decode_choice = input("\nScelta (1/2): ").strip()
            
            encoded_string = ""
            
            if decode_choice == '1':
                # Decodifica da file
                file_path = get_file_path()
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        encoded_string = file.read()
                    print(f"✓ File letto con successo: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"Errore nella lettura del file: {e}")
                    continue
                    
            elif decode_choice == '2':
                # Decodifica da input diretto
                print("\nIncolla la stringa base64 (termina con Ctrl+D su Linux/Mac o Ctrl+Z su Windows):")
                print("=" * 50)
                
                lines = []
                try:
                    while True:
                        line = input()
                        lines.append(line)
                except EOFError:
                    encoded_string = '\n'.join(lines)
                
                print("=" * 50)
                if encoded_string:
                    print(f"Stringa ricevuta ({len(encoded_string)} caratteri)")
                else:
                    print("Nessuna stringa ricevuta.")
                    continue
            else:
                print("Scelta non valida.")
                continue
            
            if encoded_string:
                # Rimuove eventuali spazi bianchi e newline extra
                encoded_string = ''.join(encoded_string.splitlines())
                
                # Suggerisci un nome file di default
                default_output = "file_decodificato.bin"
                output_path = input(f"\nInserisci il percorso di output (premi Invio per '{default_output}'): ").strip()
                
                if not output_path:
                    output_path = default_output
                
                # Decodifica e salva
                print("\nDecodifica in corso...")
                if decode_base64_to_file(encoded_string, output_path):
                    print(f"✓ File decodificato con successo!")
                    print(f"Salvato come: {output_path}")
                    
                    # Mostra informazioni sul file
                    if os.path.exists(output_path):
                        size = os.path.getsize(output_path)
                        print(f"Dimensioni: {size} bytes")
        
        elif choice == '3':
            print("\nArrivederci!")
            break
        
        else:
            print("\nScelta non valida. Riprova.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgramma interrotto dall'utente.")
    except Exception as e:
        print(f"\nSi è verificato un errore imprevisto: {e}")
