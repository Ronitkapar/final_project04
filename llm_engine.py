import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_script(text_content, model_name='gemini-1.5-flash'):
    """
    Generates a video script from the provided text content using Google Gemini.
    
    Args:
        text_content (str): The source text to analyze.
        model_name (str): The Gemini model to use.
        
    Returns:
        tuple: (list of dicts, error message)
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    model = genai.GenerativeModel(model_name)

    prompt = f"""
    You are an expert video essayist and documentarian. 
    Analyze the following text and create a compelling video script.
    
    **CRITICAL INSTRUCTION:** Break the script into MANY short scenes. 
    Each scene must be between **5 to 10 seconds** long. 
    Do not write long paragraphs. Split long sentences into multiple scenes.
    
    The output MUST be a strictly valid JSON string representing a list of scenes.
    
    Each scene in the list should be a dictionary with the following keys:
    - "scene_id": Integer, sequential starting from 1.
    - "text": String, the narration script for this scene. Keep it engaging and concise.
    - "stock_video_query": String, a concise 1-3 word search query to find a relevant stock video on Pexels (e.g., "ocean waves", "corporate meeting", "forest drone").
    - "duration_estimate": Integer, estimated duration in seconds (aim for 5-10).
    
    Text to analyze:
    {text_content[:30000]}
    """

    try:
        # Use JSON mode for reliability
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        response_text = response.text.strip()
        
        # Clean up potential markdown code blocks if the model ignores the instruction (less likely with JSON mode but good safety)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        script_data = json.loads(response_text)
        return script_data, None

    except json.JSONDecodeError as e:
        error_msg = f"JSON Decode Error: {e}\nRaw Output: {response_text}"
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Gemini API Error: {e}"
        print(error_msg)
        return None, error_msg
