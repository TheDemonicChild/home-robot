from elevenlabs.client import ElevenLabs
import json


# Load the API key from config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Set the ElevenLabs API key
client = ElevenLabs(
    api_key=config["ELEVEN_LABS_API_KEY"],
)

response = client.voices.get_all()
audio = client.generate(text="Hello there!", voice=response.voices[0])
print(response.voices)