import requests
import os
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

models = [
    "prompthero/openjourney-v4",
    "stabilityai/stable-diffusion-3-medium-diffusers",
    "gpt2" 
]

urls = [
    "https://api-inference.huggingface.co/models",
    "https://router.huggingface.co/models"
]

prompt = "A beautiful sunset over a mountain range"

print(f"Testing with Token: {HF_API_TOKEN[:5]}...")

for model in models:
    for base_url in urls:
        url = f"{base_url}/{model}"
        print(f"Testing {url}...")
        try:
            response = requests.post(url, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                print(f"SUCCESS! {url} works.")
                # Save a tiny file to prove it
                with open("test_image.png", "wb") as f:
                    f.write(response.content)
                exit(0)
            else:
                print(f"Failed: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
