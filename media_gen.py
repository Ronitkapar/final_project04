import os
import time
import asyncio
import edge_tts
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_API_URL = "https://api.pexels.com/videos/search"

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

def download_pexels_video(query, output_filename):
    """
    Searches for a video on Pexels and downloads it.
    
    Args:
        query (str): Search query for the video.
        output_filename (str): Path to save the video file.
        
    Returns:
        tuple: (success (bool), error_message (str))
    """
    if not PEXELS_API_KEY:
        return False, "PEXELS_API_KEY not found."

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape",
        "size": "medium" # Use medium to save bandwidth/storage
    }

    try:
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("videos"):
                video_data = data["videos"][0]
                video_files = video_data.get("video_files", [])
                
                # Find the best quality video file (e.g., HD)
                # Sort by width to get decent quality
                video_files.sort(key=lambda x: x.get("width", 0), reverse=True)
                
                # Pick the first one (highest res) or a specific quality if available
                best_video = video_files[0]
                download_link = best_video.get("link")
                
                if download_link:
                    video_response = requests.get(download_link, stream=True)
                    if video_response.status_code == 200:
                        with open(output_filename, "wb") as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        return True, None
                    else:
                        return False, f"Failed to download video file: {video_response.status_code}"
                else:
                    return False, "No download link found for video."
            else:
                return False, f"No videos found for query: {query}"
        else:
            return False, f"Pexels API Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Exception requesting video: {e}"
