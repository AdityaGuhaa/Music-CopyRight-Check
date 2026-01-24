from acrcloud.recognizer import ACRCloudRecognizer

# configure with your keys
config = {
    'host': 'YOUR_HOST',
    'access_key': 'YOUR_KEY',
    'access_secret': 'YOUR_SECRET',
    'timeout': 10
}

rec = ACRCloudRecognizer(config)

result = rec.recognize_by_file("test_song.wav", 0)
print(result)
