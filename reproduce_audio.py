
import asyncio
import media_gen
import os

async def test_audio():
    try:
        print("Testing Audio Generation...")
        await media_gen.generate_audio("Hello World", "test_audio.mp3")
        if os.path.exists("test_audio.mp3"):
            print("Audio generated successfully.")
            os.remove("test_audio.mp3")
        else:
            print("Audio generation failed: File not created.")
    except Exception as e:
        print(f"Error generating audio: {e}")

if __name__ == "__main__":
    asyncio.run(test_audio())
