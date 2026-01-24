import json
from acrcloud.recognizer import ACRCloudRecognizer
import os

# Debug prints (keep for now)
print("ACR HOST:", os.getenv("ACRCLOUD_HOST"))
print("ACR KEY:", os.getenv("ACRCLOUD_KEY"))
print("ACR credentials loaded")

config = {
    'host': os.getenv("ACRCLOUD_HOST"),
    'access_key': os.getenv("ACRCLOUD_KEY"),
    'access_secret': os.getenv("ACRCLOUD_SECRET"),
    'timeout': 10
}

rec = ACRCloudRecognizer(config)

def recognize_file(file_path: str):
    result = rec.recognize_by_file(file_path, 0)
    return json.loads(result)
