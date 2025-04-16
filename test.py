import os
from pathlib import Path

clip_path = "models/llava/mmproj-model-f16.gguf"
print(f"Testing CLIP file: {clip_path}")

if os.path.exists(clip_path):
    print(f"File exists, size: {os.path.getsize(clip_path) / (1024*1024):.2f} MB")
    with open(clip_path, "rb") as f:
        # Just try to read a small part of it
        data = f.read(1024)
        print(f"Successfully read {len(data)} bytes from file")
else:
    print("File not found")