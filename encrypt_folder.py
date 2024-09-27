import os
import sys
import argparse
import time
import json
from cryptography.fernet import Fernet


# Process: 
# 1. Create a mapping file that would hold the mapping of the original file name to the encrypted file name
# 2. The mapping file should be in the same folder as the encrypted files . Its name should be the same name as the folder but with a .map extension
# 3. The mapping file should itself be encrypted at the end
# 4. During decryption, the mapping file should be decrypted first and then used to decrypt the rest of the files
# 5. The original filenames with extension should be used during decryption


# Function to generate a key and save it to a file
def generate_key(key_file='key.key'):
    key = Fernet.generate_key()
    with open(key_file, 'wb') as key_out:
        key_out.write(key)
    return key

# Function to load the key from a file
def load_key(key_file='key.key'):
    return open(key_file, 'rb').read()

# Function to encrypt a file
def encrypt_file(input_file, output_file, key):
    # Check if the file is already encrypted
    if input_file.endswith('.enc'):
        raise ValueError(f"File '{input_file}' is already encrypted.")
    
    fernet = Fernet(key)
    
    # Read the file as binary data
    with open(input_file, 'rb') as file:
        original_data = file.read()
    
    # Encrypt the data
    encrypted_data = fernet.encrypt(original_data)
    
    # Write the encrypted data to a new file
    with open(output_file, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

# Function to decrypt a file
def decrypt_file(input_file, output_file, key):
    fernet = Fernet(key)
    
    # Read the encrypted file
    with open(input_file, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    
    # Decrypt the data
    decrypted_data = fernet.decrypt(encrypted_data)
    
    # Write the decrypted data to a new file
    with open(output_file, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

# Function to encrypt all files in a folder and save them to another folder
def encrypt_folder(input_folder, key):
    mapping = {}
    fernet = Fernet(key)
    
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            input_file = os.path.join(root, file)
            if input_file.endswith('.enc') or input_file.endswith('.map'):
                print(f"Skipping already encrypted file: {input_file}")
                continue
            output_file_name_only = f"{os.urandom(16).hex()}.enc"
            output_file = os.path.join(root, output_file_name_only )
            try:    
                encrypt_file(input_file, output_file, key)
                mapping[output_file_name_only] = file
                os.remove(input_file)
                print(f"Encrypted and deleted: {input_file}")
            except ValueError as e:
                print(f"Error: {str(e)}")
    
    # Create and encrypt mapping file
    map_file = os.path.join(input_folder, f"{os.path.basename(input_folder)}.map")
    print(f"Mapping file: {map_file}")
    print(f"Mapping: {mapping}")
    
    with open(map_file, 'w') as f:
        json.dump(mapping, f)
    
    with open(map_file, 'rb') as f:
        encrypted_map = fernet.encrypt(f.read())
    
    with open(map_file, 'wb') as f:
        f.write(encrypted_map)
    
    print(f"Mapping file created and encrypted: {map_file}")

# Function to decrypt all files in a folder and save them to the same folder
def decrypt_folder(input_folder, key):
    fernet = Fernet(key)
    
    # Decrypt mapping file
    map_file = os.path.join(input_folder, f"{os.path.basename(input_folder)}.map")
    with open(map_file, 'rb') as f:
        decrypted_map = fernet.decrypt(f.read())
    
    mapping = json.loads(decrypted_map.decode())
    
    for encrypted_file, original_file in mapping.items():
        print(f"Decrypting: {encrypted_file}")
        print(f"Original file: {original_file}")
        output_file = os.path.join(input_folder, original_file)
        encrypted_file = os.path.join(input_folder, encrypted_file)
        decrypt_file(encrypted_file, output_file, key)
        os.remove(encrypted_file)
        print(f"Decrypted and deleted: {encrypted_file}")
    
    # Remove the mapping file
    os.remove(map_file)
    print(f"Mapping file removed: {map_file}")

def parse_file_list(file_list):
    if file_list:
        if ',' in file_list:
            return [f.strip() for f in file_list.split(',')]
        return file_list.split()
    return None

if __name__ == '__main__':
    
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Encrypt or decrypt a folder or specific files within a folder.')
    parser.add_argument('--i', required=True, help='Path to the input folder')
    parser.add_argument('--f', help='Optional: Comma-separated or space-separated list of files relative to the input folder')
    parser.add_argument('--op', choices=['e', 'd'], required=True, help='Operation to perform (e: encrypt, d: decrypt)')
    
    args = parser.parse_args()

    input_folder = args.i
    operation = args.op

    
    # Generate or load encryption key
    key_file = '../key.key'
    
    if not os.path.exists(key_file):
        key = generate_key(key_file)
        print(f"Encryption key generated and saved to '{key_file}'.")
    else:
        key = load_key(key_file)
        print(f"Encryption key loaded from '{key_file}'.")
    
    # Perform the requested operation
    if not args.f:
        # Process entire folder
        if operation == 'e':
            encrypt_folder(input_folder, key)
            print(f"Folder encrypted: {input_folder}")
        else:  # decrypt
            decrypt_folder(input_folder, key)
            print(f"Folder decrypted: {input_folder}")
    else:
        # Process specified files
        files = parse_file_list(args.f)
        mapping = {}
        fernet = Fernet(key)
        
        for file in files:
            full_path = os.path.join(input_folder, file)
            if operation == 'e':
                if full_path.endswith('.enc'):
                    print(f"Skipping already encrypted file: {full_path}")
                    continue
                output_file = os.path.join(input_folder, f"{os.urandom(16).hex()}.enc")
                try:
                    encrypt_file(full_path, output_file, key)
                    mapping[output_file] = file
                    os.remove(full_path)
                    print(f"Encrypted and deleted: {full_path}")
                except ValueError as e:
                    print(f"Error: {str(e)}")
            else:  # decrypt
                # Decryption for individual files is not supported with the new mapping system
                print("Decryption of individual files is not supported. Please decrypt the entire folder.")
                sys.exit(1)
        
        if operation == 'e':
            # Create and encrypt mapping file
            map_file = os.path.join(input_folder, f"{os.path.basename(input_folder)}.map")
            with open(map_file, 'w') as f:
                json.dump(mapping, f)
            
            with open(map_file, 'rb') as f:
                encrypted_map = fernet.encrypt(f.read())
            
            with open(map_file, 'wb') as f:
                f.write(encrypted_map)
            
            print(f"Mapping file created and encrypted: {map_file}")

    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")
