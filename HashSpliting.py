import hashlib
import os
import json
import logging
from datetime import datetime

# Logging configuration
log_file = '/home/hprajap2/PoR_Scripts/process.log'
logging.basicConfig(filename=log_file,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file):
    """Load configuration from a JSON file."""
    logging.info(f"Loading configuration from {config_file}")
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def split_file_into_blocks(file_path, block_size, output_folder):
    """Split the file into blocks and store them."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(file_path, 'rb') as file:
        block_number = 0
        while True:
            data_block = file.read(block_size)
            if not data_block:
                break
            output_file_path = f"{output_folder}/{os.path.basename(file_path)}_block_{block_number}.bin"
            with open(output_file_path, 'wb') as output_file:
                output_file.write(data_block)
            block_number += 1
            logging.info(f"Stored block {block_number} for {file_path} at {output_file_path}")

def hash_block(block_path):
    """Generate SHA-256 hash for a given block."""
    sha256 = hashlib.sha256()
    with open(block_path, 'rb') as block_file:
        while True:
            data = block_file.read(1024 * 64)  # Read in chunks (64KB)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def hash_all_blocks(output_folder, output_folder_hash):
    """Hash all blocks in the output folder and store the hashes."""
    if not os.path.exists(output_folder_hash):
        os.makedirs(output_folder_hash)

    block_hashes = {}
    for block_file in os.listdir(output_folder):
        block_path = os.path.join(output_folder, block_file)
        if os.path.isfile(block_path):
            block_hash = hash_block(block_path)
            block_hashes[block_file] = block_hash
            logging.info(f"Block {block_file} hash: {block_hash}")

    hash_file_path = os.path.join(output_folder_hash, 'block_hashes.txt')
    with open(hash_file_path, 'w') as hash_file:
        for block_file, block_hash in block_hashes.items():
            hash_file.write(f"{block_file}: {block_hash}\n")
    
    logging.info(f"Hashes stored in {hash_file_path}")

def process_all_files(input_folder, block_size, output_folder, output_folder_hash):
    """Process all files in the input folder."""
    logging.info(f"Processing all files in {input_folder}")
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        if os.path.isfile(file_path):
            file_output_folder = os.path.join(output_folder, os.path.splitext(file_name)[0])
            split_file_into_blocks(file_path, block_size, file_output_folder)
            hash_all_blocks(file_output_folder, output_folder_hash)

if __name__ == "__main__":
    # Load configuration
    config = load_config('config.json')

    # Extract configuration parameters
    input_folder = config['input_folder']
    block_size = config['block_size']
    output_folder = config['output_folder']
    output_folder_hash = config['output_folder_hash']

    # Process all files in the input folder
    process_all_files(input_folder, block_size, output_folder, output_folder_hash)


