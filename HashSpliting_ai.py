import hashlib
import os
import json
import time

# Configuration
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)
S3_BUCKET = config["s3_bucket"]
FILE_PATH = config["input_folder"]  
BLOCK_SIZE = 64  
OUTPUT_FOLDER = config["output_folder"]
HASH_OUTPUT_FOLDER = os.path.join(OUTPUT_FOLDER, "hash")
METADATA_FILE = os.path.join(OUTPUT_FOLDER, "metadata.json")

# Ensure output directories exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(HASH_OUTPUT_FOLDER, exist_ok=True)

def hash_block(data):
    """Generate SHA-256 hash for a given block of data."""
    return hashlib.sha256(data).hexdigest()

def split_and_hash_file():
    """Splits a file, computes hashes, and stores metadata for AI analysis."""
    metadata = []
    with open(FILE_PATH, "rb") as file:
        block_num = 0
        while True:
            block = file.read(BLOCK_SIZE)
            if not block:
                break
            
            # Compute hash
            block_hash = hash_block(block)
            timestamp = time.time()  # Store access time
            
            # Save block to file
            block_filename = f"{OUTPUT_FOLDER}/block_{block_num}.bin"
            with open(block_filename, "wb") as bf:
                bf.write(block)

            # Save hash to file
            hash_filename = f"{HASH_OUTPUT_FOLDER}/block_{block_num}.hash"
            with open(hash_filename, "w") as hf:
                hf.write(block_hash)

            # Store metadata for AI-based anomaly detection
            metadata.append({
                "block_index": block_num,
                "hash": block_hash,
                "block_size": len(block),
                "timestamp": timestamp
            })
            
            print(f"✅ Block {block_num}: {block_hash}")
            block_num += 1

    # Save metadata to JSON
    with open(METADATA_FILE, "w") as meta_file:
        json.dump(metadata, meta_file, indent=4)

    print("\n✅ File splitting, hashing, and metadata logging completed!")

# Run the script
split_and_hash_file()

