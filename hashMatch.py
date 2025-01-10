import hashlib
import os

# Split the file into blocks
def split_file_into_blocks(file_path, block_size):
    """Yield blocks of the file."""
    with open(file_path, 'rb') as file:
        while True:
            block = file.read(block_size)
            if not block:
                break
            yield block

# Generate SHA-256 hash for each block
def generate_sha256_hash(data_block):
    """Generate SHA-256 hash of a data block."""
    sha256 = hashlib.sha256()
    sha256.update(data_block)
    return sha256.hexdigest()

# Load stored hashes from a file
def load_stored_hashes(stored_hash_file):
    """Load stored hashes from a file into a dictionary."""
    block_hashes = {}
    with open(stored_hash_file, 'r') as f:
        for line in f:
            block_name, block_hash = line.strip().split(": ")
            block_hashes[block_name] = block_hash
    return block_hashes

# Verify file integrity by comparing retrieved file's blocks with stored hashes
def verify_file_integrity(retrieved_file, stored_hash_file, block_size):
    """Verify the integrity of a retrieved file using SHA-256 hashes."""
    block_number = 0

    # Load the stored hashes
    stored_hashes = load_stored_hashes(stored_hash_file)
    
    if not stored_hashes:
        print(f"No hashes found in {stored_hash_file}.")
        return False

    # Split the retrieved file into blocks and compare hashes
    for block in split_file_into_blocks(retrieved_file, block_size):
        block_hash = generate_sha256_hash(block)
        block_name = f"{os.path.basename(retrieved_file)}_block_{block_number}.bin"

        # Check if the block hash matches the stored hash
        if block_name not in stored_hashes:
            print(f"No stored hash found for block: {block_name}")
            return False
        
        if block_hash != stored_hashes[block_name]:
            print(f"Block {block_name} hash mismatch! Retrieved hash: {block_hash}, Stored hash: {stored_hashes[block_name]}")
            return False
        
        print(f"Block {block_name} verified successfully.")
        block_number += 1

    print("All blocks validated successfully. File integrity verified.")
    return True

if __name__ == "__main__":
    # Paths to the retrieved file and stored hash file
    retrieved_file = input("Enter the path to the retrieved file: ")
    stored_hash_file = input("Enter the path to the stored hash file: ")

    # Block size (should be the same as used during upload)
    block_size = int(input("Enter the block size used for splitting (in bytes): "))

    # Validate the file
    if os.path.exists(retrieved_file) and os.path.exists(stored_hash_file):
        print("Verifying file integrity...")
        if verify_file_integrity(retrieved_file, stored_hash_file, block_size):
            print("File integrity verified successfully.")
        else:
            print("File integrity verification failed.")
    else:
        print("One or both files do not exist.")

