import ipfshttpclient
import hashlib
import os

# Connect to the local IPFS daemon
client = ipfshttpclient.connect('/dns/localhost/tcp/5001/http')

# Function to split the file into blocks and store on IPFS
def split_and_store_on_ipfs(file_path, block_size=64):
    # Open the file
    with open(file_path, 'rb') as f:
        block_num = 0
        while True:
            block = f.read(block_size)
            if not block:
                break
            # Hash the block and upload it to IPFS
            block_hash = hashlib.sha256(block).hexdigest()
            # Upload block to IPFS
            res = client.add_bytes(block)
            # Save the CID (Content Identifier)
            print(f"Block {block_num}: {block_hash} - CID: {res}")
            block_num += 1

# Test the function with your file
split_and_store_on_ipfs('/path/to/your/file.txt')

