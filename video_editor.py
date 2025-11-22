import os
import PIL.Image

# Monkey-patch ANTIALIAS for Pillow 10+ compatibility
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
    vfx
)

def create_video(audio_files, image_files, output_file="final_video.mp4"):
    """
    Creates a video by combining audio and images with a Ken Burns effect.
    
    Args:
        audio_files (list): List of paths to audio files.
        image_files (list): List of paths to image files.
        output_file (str): Path to save the final video.
        
    Returns:
        str: Path to the generated video file.
    """
    clips = []
    
    if len(audio_files) != len(image_files):
        return None, "Error: Number of audio files and image files must match."

    for audio_path, image_path in zip(audio_files, image_files):
        try:
            # Load Audio
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Load Image
            image_clip = ImageClip(image_path).set_duration(duration)
            
            # Resize to standard HD height (1080p) to ensure quality before effects
            # We assume landscape images for simplicity, or we can force a ratio.
            # Let's resize to height 1080, maintaining aspect ratio.
            image_clip = image_clip.resize(height=1080)
            
            # Center Crop to 16:9 aspect ratio (1920x1080)
            # This ensures we have a standard frame to work with
            image_clip = image_clip.crop(x1=None, y1=None, x2=None, y2=None, 
                                         width=1920, height=1080, 
                                         x_center=image_clip.w/2, y_center=image_clip.h/2)

            # Ken Burns Effect: Zoom In
            # We will zoom from 1.0 to 1.15 over the duration for more visible motion
            def zoom_in(t):
                return 1.0 + 0.15 * (t / duration)
            
            # Apply resize (zoom) effect
            # We need to resize and then keep it centered. 
            # MoviePy's resize with a function does exactly this.
            zoomed_clip = image_clip.resize(zoom_in)
            
            # After zooming, the clip is larger than 1920x1080. 
            # We need to composite it on a 1920x1080 background (or just crop it again).
            # CompositeVideoClip is safer to ensure final dimensions.
            # 'center' position keeps it centered.
            final_clip = CompositeVideoClip([zoomed_clip.set_position('center')], size=(1920, 1080))
            final_clip = final_clip.set_duration(duration)
            final_clip = final_clip.set_audio(audio_clip)
            
            clips.append(final_clip)
            
        except Exception as e:
            print(f"Error processing scene {audio_path}: {e}")
            return None, f"Error processing scene {os.path.basename(audio_path)}: {e}"

    if not clips:
        return None, "No clips were successfully created."

    try:
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        return output_file, None
    except Exception as e:
        print(f"Error rendering final video: {e}")
        return None, f"Error rendering final video: {e}"
