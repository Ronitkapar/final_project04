import streamlit as st
import os
import asyncio
import tempfile
from dotenv import load_dotenv

# Import our modules
import utils
import llm_engine
import media_gen
import video_editor

# Load environment variables
load_dotenv()

import random

# Set page config
st.set_page_config(page_title="AI Video Storyteller", page_icon="🎬", layout="wide")

# Custom CSS for Premium Design
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF914D);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    .stProgress > div > div > div > div {
        background-color: #FF4B4B;
    }
    .css-1d391kg {
        background-color: #1f2937;
        border-radius: 10px;
        padding: 1rem;
    }
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🎬 AI Video Storyteller")
    st.markdown("### Turn your documents into cinematic video essays.")

    # Sidebar for Configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Model Selection
        model_options = [
            "gemini-2.0-flash-lite",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-2.5-flash-lite",
            "gemini-3-pro-preview"
        ]
        selected_model = st.selectbox("Select Gemini Model", model_options, index=0)
        
        st.divider()
        st.info("API Keys are loaded securely from environment variables.")

    # Main Content Area
    uploaded_file = st.file_uploader("Upload a PDF or Text file", type=["pdf", "txt"])

    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        if st.button("Generate Video", type="primary"):
            if not os.getenv("GOOGLE_API_KEY") or not os.getenv("HF_API_TOKEN"):
                st.error("Missing API Keys in .env file.")
                return

            # Create a temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Phase 1: Analyze Text
                status_text.markdown("**Phase 1: Analyzing Document...**")
                text_content = ""
                if uploaded_file.name.endswith(".pdf"):
                    text_content = utils.extract_text_from_pdf(uploaded_file)
                else:
                    text_content = str(uploaded_file.read(), "utf-8")
                
                cleaned_text = utils.clean_text(text_content)
                if not cleaned_text:
                    st.error("Could not extract text from file.")
                    return
                progress_bar.progress(10)

                # Phase 2: Generate Script
                status_text.markdown(f"**Phase 2: Generating Script with {selected_model}...**")
                script_data, error = llm_engine.generate_script(cleaned_text, selected_model)
                if error:
                    st.error(f"Failed to generate script: {error}")
                    return
                
                with st.expander("View Generated Script"):
                    st.json(script_data)
                progress_bar.progress(30)

                # Phase 3: Generate Assets (Smart Generation)
                status_text.markdown("**Phase 3: Generating Audio and Visuals...**")
                audio_files = []
                image_files = []
                generated_images_pool = [] # Store paths of actually generated images
                
                total_scenes = len(script_data)
                for i, scene in enumerate(script_data):
                    scene_id = scene.get("scene_id", i+1)
                    status_text.text(f"Processing Scene {scene_id}/{total_scenes}...")
                    
                    # Audio (Always generate)
                    audio_path = os.path.join(temp_dir, f"audio_{scene_id}.mp3")
                    asyncio.run(media_gen.generate_audio(scene["text"], audio_path))
                    audio_files.append(audio_path)
                    
                    # Image (Smart Reuse Logic)
                    # Logic: 70% chance to generate new, 30% chance to reuse (if pool has images)
                    # Always generate for the first scene
                    should_generate_new = True
                    if i > 0 and generated_images_pool:
                        if random.random() > 0.7: # 30% chance to reuse
                            should_generate_new = False
                    
                    image_path = os.path.join(temp_dir, f"image_{scene_id}.png")
                    
                    if should_generate_new:
                        success, error_msg = media_gen.generate_image(scene["image_prompt"], image_path)
                        if not success:
                            st.warning(f"Failed to generate image for Scene {scene_id}: {error_msg}. Trying to reuse previous image...")
                            if generated_images_pool:
                                # Fallback to reuse if generation fails
                                import shutil
                                reuse_src = random.choice(generated_images_pool)
                                shutil.copy(reuse_src, image_path)
                                image_files.append(image_path)
                            else:
                                st.error("Critical: Image generation failed and no images to reuse.")
                                return
                        else:
                            image_files.append(image_path)
                            generated_images_pool.append(image_path)
                    else:
                        # Reuse an existing image
                        import shutil
                        reuse_src = random.choice(generated_images_pool)
                        shutil.copy(reuse_src, image_path)
                        image_files.append(image_path)
                        status_text.text(f"Reusing visual asset for Scene {scene_id}...")
                    
                    # Update progress based on scenes
                    current_progress = 30 + int((i + 1) / total_scenes * 40)
                    progress_bar.progress(current_progress)

                # Phase 4: Assemble Video
                status_text.markdown("**Phase 4: Assembling Video (Cinematic Motion)...**")
                output_video_path = "final_output.mp4"
                result, error = video_editor.create_video(audio_files, image_files, output_video_path)
                
                if error:
                    st.error(f"Failed to assemble video: {error}")
                elif result:
                    progress_bar.progress(100)
                    status_text.success("Video Generation Complete!")
                    st.balloons()
                    
                    st.video(result)
                    
                    with open(result, "rb") as file:
                        st.download_button(
                            label="Download Video",
                            data=file,
                            file_name="ai_video_essay.mp4",
                            mime="video/mp4"
                        )

if __name__ == "__main__":
    main()
