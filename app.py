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
    st.title("🎬 AI Video Storyteller (Stock Footage Edition)")
    st.markdown("### Turn your documents into cinematic video essays with Stock Footage.")

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
        st.info("API Keys (Google & Pexels) are loaded from environment variables.")

    # Main Content Area
    uploaded_file = st.file_uploader("Upload a PDF or Text file", type=["pdf", "txt"])

    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        if st.button("Generate Video", type="primary"):
            if not os.getenv("GOOGLE_API_KEY") or not os.getenv("PEXELS_API_KEY"):
                st.error("Missing API Keys in .env file (GOOGLE_API_KEY or PEXELS_API_KEY).")
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

                # Phase 3: Generate Assets (Audio & Stock Video)
                status_text.markdown("**Phase 3: Fetching Stock Footage & Generating Audio...**")
                audio_files = []
                video_files = []
                text_scripts = []
                
                total_scenes = len(script_data)
                for i, scene in enumerate(script_data):
                    scene_id = scene.get("scene_id", i+1)
                    status_text.text(f"Processing Scene {scene_id}/{total_scenes}...")
                    
                    # Store text for subtitles
                    text_scripts.append(scene["text"])

                    # Audio
                    audio_path = os.path.join(temp_dir, f"audio_{scene_id}.mp3")
                    asyncio.run(media_gen.generate_audio(scene["text"], audio_path))
                    audio_files.append(audio_path)
                    
                    # Stock Video (Pexels)
                    video_path = os.path.join(temp_dir, f"video_{scene_id}.mp4")
                    query = scene.get("stock_video_query", "abstract background")
                    
                    success, error_msg = media_gen.download_pexels_video(query, video_path)
                    if not success:
                        st.warning(f"Scene {scene_id}: {error_msg}. Using fallback.")
                        # Video editor handles missing files as black screen, 
                        # but we could also download a default fallback here if we wanted.
                    
                    video_files.append(video_path)
                    
                    # Update progress based on scenes
                    current_progress = 30 + int((i + 1) / total_scenes * 40)
                    progress_bar.progress(current_progress)

                # Phase 4: Assemble Video
                status_text.markdown("**Phase 4: Assembling Video (Subtitles & Clips)...**")
                output_video_path = "final_output.mp4"
                
                # Note: Updated video_editor.create_video signature
                result, error = video_editor.create_video(audio_files, video_files, text_scripts, output_video_path)
                
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
                            file_name="ai_stock_video.mp4",
                            mime="video/mp4"
                        )

if __name__ == "__main__":
    main()
