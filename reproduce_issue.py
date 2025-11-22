
import os
from moviepy.editor import TextClip

def test_text_clip():
    try:
        print("Testing TextClip...")
        txt_clip = TextClip("Hello World", fontsize=70, color='white')
        print("TextClip created successfully.")
    except Exception as e:
        print(f"Error creating TextClip: {e}")

if __name__ == "__main__":
    test_text_clip()
