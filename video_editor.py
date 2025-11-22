import os
import textwrap
import PIL.Image

# Monkey-patch ANTIALIAS for Pillow 10+ compatibility
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
    vfx
)
from moviepy.config import change_settings

# Try to detect ImageMagick (required for TextClip)
# On Render/Linux, it's usually just 'convert' or 'magick'
# If not found, TextClip might fail.
# change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"}) 

def create_video(audio_paths, video_paths, text_scripts, output_path):
    """
    Assembles video clips, audio, and subtitles into a final video.
    
    Args:
        audio_paths (list): List of paths to audio files.
        video_paths (list): List of paths to video files.
        text_scripts (list): List of narration text strings for subtitles.
        output_path (str): Path to save the final video.
        
    Returns:
        tuple: (output_path (str) or None, error_message (str) or None)
    """
    try:
        clips = []
        
        for i, (audio_path, video_path, text) in enumerate(zip(audio_paths, video_paths, text_scripts)):
            try:
                # Load Audio
                if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                     print(f"Skipping scene {i+1}: Invalid audio file {audio_path}")
                     continue

                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                
                # Load Video
                if os.path.exists(video_path):
                    video_clip = VideoFileClip(video_path)
                    # Resize/Crop to 1920x1080 (Landscape)
                    # First resize to cover 1920x1080
                    target_ratio = 16/9
                    current_ratio = video_clip.w / video_clip.h
                    
                    if current_ratio > target_ratio:
                        # Too wide, resize by height
                        video_clip = video_clip.resize(height=1080)
                    else:
                        # Too tall/square, resize by width
                        video_clip = video_clip.resize(width=1920)
                        
                    # Crop center
                    video_clip = video_clip.crop(x1=video_clip.w/2 - 960, y1=video_clip.h/2 - 540, 
                                                 width=1920, height=1080)
                else:
                    # Fallback: Solid Color
                    print(f"Video file missing for scene {i+1}, using fallback.")
                    video_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)

                # Loop video if shorter than audio
                if video_clip.duration < duration:
                    video_clip = video_clip.loop(duration=duration)
                else:
                    video_clip = video_clip.subclip(0, duration)
                
                video_clip = video_clip.set_audio(audio_clip)
                
                # Create Subtitles
                # Wrap text to fit screen width (approx 50 chars for 1920px with large font)
                wrapped_text = textwrap.fill(text, width=50)
                
                txt_clip = TextClip(
                    wrapped_text, 
                    fontsize=70, 
                    color='white', 
                    font='Arial-Bold', 
                    stroke_color='black', 
                    stroke_width=3,
                    method='caption',
                    size=(1800, None), # Constrain width
                    align='center'
                ).set_pos(('center', 'bottom')).set_duration(duration).margin(bottom=50, opacity=0)
                
                # Composite Video + Text
                final_scene_clip = CompositeVideoClip([video_clip, txt_clip])
                clips.append(final_scene_clip)
                
            except Exception as e:
                return None, f"Error processing scene {i+1}: {str(e)}"
        
        # Concatenate all clips
        if not clips:
            return None, "No valid scenes to assemble. All scenes were skipped or failed."

        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        return output_path, None

    except Exception as e:
        return None, str(e)
