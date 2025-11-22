import os
import time
import asyncio
import edge_tts
import requests
from dotenv import load_dotenv

load_dotenv()

from huggingface_hub import InferenceClient

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
# We don't need a hardcoded URL anymore, InferenceClient handles it.
# We can specify the model directly in the client or the call.
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

async def generate_audio(text, output_filename, voice="en-US-ChristopherNeural"):
    """
    Generates audio from text using Edge TTS.
    
    Args:
        text (str): The text to convert to speech.
        output_filename (str): Path to save the audio file.
        voice (str): The voice to use.
    """
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_filename)
    except Exception as e:
        print(f"Error generating audio: {e}")

def generate_image(prompt, output_filename):
    """
    Generates an image from a text prompt using HuggingFace Inference API.
    
    Args:
        prompt (str): The image description.
        output_filename (str): Path to save the image file.
        
    Returns:
        tuple: (success (bool), error_message (str))
    """
    if not HF_API_TOKEN:
        return False, "HF_API_TOKEN not found."

    # Enforce landscape/cinematic style
    enhanced_prompt = f"{prompt}, cinematic, 8k, landscape, wide shot, 16:9 aspect ratio, highly detailed"
    negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy, watermark, text, deformed, glitch, lowres, bad hands"

    client = InferenceClient(token=HF_API_TOKEN)

    try:
        # text_to_image returns a PIL Image
        image = client.text_to_image(enhanced_prompt, negative_prompt=negative_prompt, model=MODEL_ID)
        image.save(output_filename)
        return True, None
            
    except Exception as e:
        error_msg = f"Exception requesting image: {e}"
        print(error_msg)
        return False, error_msg
