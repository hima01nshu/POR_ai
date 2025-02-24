import os
import boto3
import hashlib
import json
from botocore.exceptions import NoCredentialsError, ClientError

# Load configuration
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)

S3_BUCKET = config["s3_bucket"]
LOCAL_DIR = config["local_directory"]
HASH_DIR = config["hash_directory"]
BACKUP_DIR = config.get("backup_directory", None)

s3_client = boto3.client('s3')

def calculate_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except FileNotFoundError:
        return None

def verify_file_integrity(file_name):
    """Check if file's hash matches the stored hash."""
    local_file = os.path.join(LOCAL_DIR, file_name)
    hash_file = os.path.join(HASH_DIR, file_name + ".sha256")
    
    if not os.path.exists(local_file):
        print(f"[MISSING] {file_name} not found locally.")
        return False
    
    if not os.path.exists(hash_file):
        print(f"[WARNING] No stored hash for {file_name}, skipping.")
        return True
    
    with open(hash_file, 'r') as f:
        stored_hash = f.read().strip()
    
    computed_hash = calculate_sha256(local_file)
    
    if computed_hash != stored_hash:
        print(f"[CORRUPT] {file_name} integrity check failed!")
        return False
    
    print(f"[OK] {file_name} integrity verified.")
    return True

def restore_from_s3(file_name):
    """Attempt to restore a file from S3."""
    try:
        local_file = os.path.join(LOCAL_DIR, file_name)
        s3_client.download_file(S3_BUCKET, file_name, local_file)
        print(f"[RECOVERED] {file_name} restored from S3.")
    except NoCredentialsError:
        print("[ERROR] AWS credentials not found.")
    except ClientError as e:
        print(f"[ERROR] Unable to restore {file_name} from S3: {e}")

def restore_from_backup(file_name):
    """Restore file from a local backup if available."""
    if not BACKUP_DIR:
        print("[SKIP] No backup directory configured.")
        return
    
    backup_file = os.path.join(BACKUP_DIR, file_name)
    local_file = os.path.join(LOCAL_DIR, file_name)
    
    if os.path.exists(backup_file):
        os.system(f"cp {backup_file} {local_file}")
        print(f"[RECOVERED] {file_name} restored from local backup.")
    else:
        print(f"[FAIL] {file_name} not found in backup directory.")

def run_self_healing():
    """Main function to check and recover files."""
    for file_name in os.listdir(HASH_DIR):
        if file_name.endswith(".sha256"):
            original_file = file_name.replace(".sha256", "")
            if not verify_file_integrity(original_file):
                print(f"[ACTION] Attempting recovery for {original_file}")
                restore_from_s3(original_file)
                if not verify_file_integrity(original_file):
                    restore_from_backup(original_file)

if __name__ == "__main__":
    run_self_healing()

