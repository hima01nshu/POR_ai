import hashlib
import os

# Verify file integrity using SHA-256
def verify_file_integrity(file_path, hash_file_path):
    """Verify the integrity of a file using its SHA-256 hash."""
    # Calculate the hash of the file
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    calculated_hash = sha256.hexdigest()

    # Read the expected hash from the hash file
    with open(hash_file_path, 'r') as f:
        expected_hash = f.read().strip()

    return calculated_hash == expected_hash

if __name__ == "__main__":
    # Prompt the user for input and hash file locations
    retrieved_file = input("Enter the path to the retrieved file: ")
    hash_file = input("Enter the path to the hash file: ")

    # Check file integrity
    if os.path.exists(retrieved_file) and os.path.exists(hash_file):
        print("Checking file integrity...")
        if verify_file_integrity(retrieved_file, hash_file):
            print("File integrity verified successfully.")
        else:
            print("File integrity verification failed.")
    else:
        print("One or both files do not exist.")

