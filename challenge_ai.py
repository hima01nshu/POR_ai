import hashlib
import os
import json

# Load configuration from config.json
CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from a JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Configuration file '{CONFIG_FILE}' not found.")
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def calculate_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""
    try:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"[ERROR] Could not read {file_path}: {e}")
        return None

def verify_file_integrity(retrieved_file, hash_file):
    """Verify the integrity of a file using its SHA-256 hash."""
    calculated_hash = calculate_sha256(retrieved_file)
    if calculated_hash is None:
        return False
    
    try:
        with open(hash_file, 'r') as f:
            expected_hash = f.read().strip()
        return calculated_hash == expected_hash
    except Exception as e:
        print(f"[ERROR] Could not read hash file {hash_file}: {e}")
        return False

def main():
    """Main function to verify file integrity."""
    config = load_config()
    if not config:
        return

    retrieved_dir = config.get("retrieved_files", "")
    hash_dir = config.get("hash_files", "")

    if not os.path.exists(retrieved_dir) or not os.path.exists(hash_dir):
        print("[ERROR] One or both directories do not exist. Check config.json.")
        return

    print("[INFO] Checking file integrity...")

    all_verified = True
    for file_name in os.listdir(retrieved_dir):
        retrieved_file = os.path.join(retrieved_dir, file_name)
        hash_file = os.path.join(hash_dir, file_name + ".hash")

        if not os.path.exists(hash_file):
            print(f"[WARNING] No hash file found for {file_name}, skipping.")
            continue

        if verify_file_integrity(retrieved_file, hash_file):
            print(f"[SUCCESS] {file_name} is intact.")
        else:
            print(f"[ALERT] {file_name} integrity verification failed!")
            all_verified = False

    if all_verified:
        print("[INFO] All files verified successfully.")
    else:
        print("[ERROR] Some files failed verification. Possible corruption!")

if __name__ == "__main__":
    main()

