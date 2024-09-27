# Folder and File Encryption/Decryption Tool

This Python script provides a simple way to encrypt and decrypt folders or specific files using the Fernet symmetric encryption from the `cryptography` library.

## Features

- Encrypt/decrypt entire folders
- Encrypt/decrypt specific files within a folder
- Automatic key generation and management
- Prevention of double encryption
- Support for both comma-separated and space-separated file lists

## Requirements

- Python 3.x
- cryptography library

Install the required library using:

```bash
pip install cryptography
```

## Usage

### Basic Command Structure

- `--f`: Path to the input folder (required)
- `--o`: Operation to perform (required)
  - `e` for encryption
  - `d` for decryption
- `--files`: Optional list of specific files to process (relative to the input folder)

### Examples


1. Encrypt an entire folder:
   ```
   python encrypt_folder.py --i /path/to/folder --o e
   ```

2. Decrypt an entire folder:
   ```
   python encrypt_folder.py --i /path/to/folder --o d
   ```

3. Encrypt specific files in a folder (comma-separated):
   ```
   python encrypt_folder.py --i /path/to/folder --o e --f file1.txt,file2.pdf,file3.docx
   ```

4. Decrypt specific files in a folder (space-separated, use quotes):
   ```
   python encrypt_folder.py --i /path/to/folder --o d --f "file1.txt.enc file2.pdf.enc file3.docx.enc"
   ```

## Key Management

- The script automatically generates a key file (`key.key`) in the same directory if it doesn't exist.
- The same key is used for both encryption and decryption.
- Keep the `key.key` file secure and in the same directory as the script for successful operation.

## Notes

- Encrypted files will have a `.enc` extension added to their original filename.
- The script prevents double encryption by skipping files that already have a `.enc` extension.
- Original files are deleted after successful encryption or decryption.
- The script provides execution time information upon completion.

## Caution

- Always ensure you have backups of your data before using this tool.
- Keep your `key.key` file secure. If lost, encrypted files cannot be recovered.


