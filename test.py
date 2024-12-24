import json
from openai import OpenAI
import base64
from PIL import Image
from io import BytesIO

# Load the API key from config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Initialize the OpenAI client
client = OpenAI(api_key=config["CHATGPT_API_KEY"])

def compress_image(image_path):
    with Image.open(image_path) as img:
        img = img.resize((800, 800))  # Resize to 800x800 pixels
        
        # Save the thumbnail locally
        img.save("images/1.thumb.jpg", format="JPEG", quality=85)
        
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)  # Adjust quality
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

def send_image_analysis_request(prompt, image_path):
    try:
        # Compress and encode the image
        base64_image = compress_image(image_path)
        
        # Make the API request using the OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_completion_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    user_prompt = "What is this an image of?"
    image_path = "images/1.jpg"  # Replace with the path to your image file
    answer = send_image_analysis_request(user_prompt, image_path)
    print("ChatGPT says:", answer)