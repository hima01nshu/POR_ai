import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Load metadata
with open("output/metadata.json", "r") as file:
    metadata = json.load(file)

# Convert metadata to DataFrame
df = pd.DataFrame(metadata)

# Normalize timestamps (convert to relative time differences)
df["time_diff"] = df["timestamp"].diff().fillna(0)

# Select features for anomaly detection
features = ["block_size", "time_diff"]
X = df[features]

# Train Isolation Forest model
model = IsolationForest(contamination=0.1, random_state=42)
df["anomaly"] = model.fit_predict(X)

# Print results
for index, row in df.iterrows():
    status = "🛑 Anomaly" if row["anomaly"] == -1 else "✅ Normal"
    print(f"Block {row['block_index']}: {status}")

# Save results
df.to_csv("output/anomaly_results.csv", index=False)
print("\n🔍 Anomaly detection completed! Results saved in output/anomaly_results.csv")

