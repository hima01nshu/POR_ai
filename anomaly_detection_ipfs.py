import ipfshttpclient
import hashlib

# Connect to the local IPFS daemon
client = ipfshttpclient.connect('/dns/localhost/tcp/5001/http')

# Function to verify the block using its CID
def verify_block_with_ipfs(cid, expected_hash):
    try:
        # Fetch the block from IPFS
        block_data = client.cat(cid)
        # Calculate the hash of the retrieved block
        retrieved_hash = hashlib.sha256(block_data).hexdigest()
        # Compare with the expected hash
        if retrieved_hash == expected_hash:
            print(f"✅ Block verified with CID: {cid}")
        else:
            print(f"❌ Anomaly detected in block with CID: {cid}")
    except Exception as e:
        print(f"Error retrieving block with CID {cid}: {e}")

# Test with a block's CID and expected hash
verify_block_with_ipfs("QmT7g1Vekf1zQpRzMxq3Kz8Bp4u93G57m6o6wYN1RfYj9X", "251171dc4023092b8e109bec3bcf10ec94d3496d4e2d415f2424a1a6fd6ed9d5")

