import sys
import json
from openai import OpenAI
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import sys
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from capture_photo import capture_photo
import cv2
from datetime import datetime
import time
import traceback

from utils import logger, timing  # Import the logger and timing decorator

# Import colorama for colored terminal text
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

ENABLE_ELEVEN_LABS_VOICE = False

# Load the API key from config.json
@timing
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# Initialize the OpenAI client
@timing
def init_openai_client(api_key):
    return OpenAI(api_key=api_key)

client = init_openai_client(config["CHATGPT_API_KEY"])

if ENABLE_ELEVEN_LABS_VOICE:
    # Initialize the ElevenLabs client
    @timing
    def init_elevenlabs_client(api_key):
        return ElevenLabs(api_key=api_key)
    
    config = load_config()
    EL_client = init_elevenlabs_client(config["ELEVEN_LABS_API_KEY"])

@timing
def resize_image(image_path, width=800):
    """
    Resizes the image to the specified width while maintaining aspect ratio.
    
    Args:
        image_path (str): Path to the original image.
        width (int): Desired width in pixels.
    
    Returns:
        Image.Image: Resized PIL Image object.
    """
    with Image.open(image_path) as img:
        # Calculate height to maintain aspect ratio
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio)
        
        # Use the appropriate resampling filter
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
        return resized_img

@timing
def add_bars(img, top_height=50, left_width=50, color="blue"):
    """
    Adds bars to the top and left sides of the image and overlays letters A through I on the top bar
    and numbers 1 through 9 on the left bar.
    
    Args:
        img (Image.Image): PIL Image object.
        top_height (int): Height of the top bar in pixels.
        left_width (int): Width of the left bar in pixels.
        color (str): Color of the bars.
    
    Returns:
        Image.Image: Modified PIL Image object with bars and letters/numbers added.
    """
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Add top bar
    top_bar = [(0, 0), (width, top_height)]
    draw.rectangle(top_bar, fill=color)

    # Add left bar
    left_bar = [(0, 0), (left_width, height)]
    draw.rectangle(left_bar, fill=color)

    # Define the letters to add on the top bar
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    num_letters = len(letters)

    # Define the numbers to add on the left bar
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    num_numbers = len(numbers)

    # Load a bold font. You can specify a TTF font file if available.
    try:
        # Attempt to load a truetype font (you may need to adjust the path)
        font = ImageFont.truetype("resources/ArialBlack.ttf", size=40)  # Arial Black
    except IOError:
        # Fallback to the default PIL font if the specified font is not found
        font = ImageFont.load_default()
        print("Warning: Arial Black font not found. Using default font.")

    # Add letters to the top bar
    spacing_letters = width / num_letters  # Remove the +1 to eliminate the right gap

    for i, letter in enumerate(letters):
        # Calculate the position for each letter
        x = spacing_letters * (i + 0.5)  # Center each letter within its spacing
        y = 10  # Vertically center the text in the top bar

        # Get the bounding box of the letter
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate the position to center the text
        text_x = (x - text_width / 2) + 20
        text_y = y - text_height / 2

        # Add the text to the image
        draw.text((text_x, text_y), letter, font=font, fill="white")

    # Add numbers to the left bar
    spacing_numbers = height / num_numbers  # Spacing based on the number of numbers

    for i, number in enumerate(numbers):
        # Calculate the position for each number
        x = left_width / 2  # Center horizontally in the left bar
        y = spacing_numbers * (i + 0.5)  # Center each number within its spacing

        # Get the bounding box of the number
        bbox = draw.textbbox((0, 0), number, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate the position to center the text
        text_x = x - text_width / 2
        text_y = y - text_height / 2

        # Add the text to the image
        draw.text((text_x, text_y), number, font=font, fill="white")

    return img

@timing
def save_image(img, save_path, quality=85):
    """
    Saves the PIL Image object to the specified path.
    
    Args:
        img (Image.Image): PIL Image object.
        save_path (str): Path where the image will be saved.
        quality (int): Quality of the saved image (1-100).
    """
    img.save(save_path, format="JPEG", quality=quality)

@timing
def encode_image(img, quality=85):
    """
    Encodes the PIL Image object to a base64 string.
    
    Args:
        img (Image.Image): PIL Image object.
        quality (int): Quality of the image for encoding.
    
    Returns:
        str: Base64-encoded string of the image.
    """
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

@timing
def send_image_analysis_request(prompt, image_path):
    try:
        # Ensure the 'images' directory exists
        os.makedirs("images", exist_ok=True)
        
        # Step 1: Resize the image
        resized_img = resize_image(image_path)
        
        # Step 2: Add decorative bars and letters
        modified_img = add_bars(resized_img)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Step 3: Save the modified image locally with the new filename
        save_image(modified_img, f"images/small_{timestamp}.jpg", quality=85)
        
        # Step 4: Encode the image to base64
        base64_image = encode_image(modified_img, quality=85)
        
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
        logger.error(f"Error in 'send_image_analysis_request': {str(e)}")
        return f"Error: {str(e)}"

@timing
def load_prompts():
    """
    Loads prompts from prompts/1.txt, prompts/2.txt, and prompts/3.txt.
    
    Returns:
        list: A list containing the content of each prompt file.
    """
    prompt_files = ["prompts/1.txt", "prompts/2.txt", "prompts/3.txt"]
    prompts = []
    for file in prompt_files:
        try:
            with open(file, "r") as f:
                prompts.append(f.read().strip())
        except Exception as e:
            logger.error(f"Failed to read {file}: {e}")
            prompts.append("Describe the image")  # Fallback prompt
    return prompts

@timing
def main():
    """
    Main function that processes images and sends analysis requests using prompts
    from prompts/1.txt, prompts/2.txt, and prompts/3.txt in a round-robin fashion.
    """
    prompts = load_prompts()
    prompt_count = len(prompts)
    current_prompt_index = 0  # Initialize the round-robin index

    while True:
        try:
            # Select the current prompt
            user_prompt = prompts[current_prompt_index]
            current_prompt_index = (current_prompt_index + 1) % prompt_count  # Update index for next iteration

            photo = capture_photo()
            if photo is not None:
                # Save the photo to a file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"images/{timestamp}.jpg"
                cv2.imwrite(image_path, photo)
            else:
                logger.error("Failed to capture photo.")
                continue  # Skip processing if photo capture failed

            # Analyze the image
            answer = send_image_analysis_request(user_prompt, image_path)
            
            # Print the original prompt in Blue
            print(f"{Fore.BLUE}User Prompt: {user_prompt}{Style.RESET_ALL}")
            
            # Print ChatGPT's response in Green
            print(f"{Fore.GREEN}ChatGPT says: {answer}{Style.RESET_ALL}")

            if ENABLE_ELEVEN_LABS_VOICE:
                # Say answer out loud with ElevenLabs
                audio_stream = EL_client.text_to_speech.convert_as_stream(
                    text=answer,
                    voice_id="s3Z2DZH32dW8IHJFedam",
                    model_id="eleven_flash_v2_5"
                )
                stream(audio_stream)
            else:
                logger.info("Eleven Labs voice functionality is disabled. Skipping text-to-speech.")

        except Exception as e:
            logger.error(f"An error occurred in 'main': {e}")
            logger.error(traceback.format_exc())

        # Wait for 5 seconds before the next iteration
        time.sleep(5)

if __name__ == "__main__":
    main()

