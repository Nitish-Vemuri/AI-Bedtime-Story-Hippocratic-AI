"""
Standalone Audio Generator for Bedtime Stories
Uses third-party TTS libraries (gTTS or pyttsx3) as OpenAI v0.28.0 doesn't support TTS

This is separate from main_iterative.py to keep the assignment code clean.
"""

from pathlib import Path
import os

def generate_audio_from_text(story_text: str, output_filename: str = "bedtime_story.mp3", speed: float = 0.9):
    """
    Convert story text to speech using Google Text-to-Speech (gTTS).
    
    Args:
        story_text: The story text to convert
        output_filename: Output MP3 filename
        speed: Speaking speed (0.5 = very slow, 1.0 = normal, 1.5 = fast)
               For bedtime: 0.9 recommended (slightly slower, calming)
    
    Returns:
        Path to generated audio file
    """
    try:
        from gtts import gTTS
        
        print("\n" + "="*70)
        print("GENERATING AUDIO VERSION")
        print("="*70)
        print(f"Speed: {speed}x (slower = more calming)")
        print("Converting story to speech...")
        
        # Create TTS object
        tts = gTTS(text=story_text, lang='en', slow=(speed < 0.8))
        
        # Save audio file
        audio_path = Path(output_filename)
        tts.save(str(audio_path))
        
        # Calculate estimated duration
        word_count = len(story_text.split())
        duration_minutes = (word_count / 150) / speed
        
        print(f"\n✅ Audio file saved: {audio_path.absolute()}")
        print(f"📊 Word count: {word_count}")
        print(f"⏱️  Estimated duration: {duration_minutes:.1f} minutes")
        print("="*70)
        
        return str(audio_path.absolute())
        
    except ImportError:
        print("\n❌ gTTS library not installed!")
        print("\nTo enable audio generation, run:")
        print("  pip install gTTS")
        print("\nThen run this script again.")
        return None
    except Exception as e:
        print(f"\n❌ Error generating audio: {e}")
        return None


def main():
    """Interactive mode: paste a story and generate audio."""
    print("\n" + "🎵" * 35)
    print("  Bedtime Story Audio Generator")
    print("  Powered by OpenAI Text-to-Speech")
    print("🎵" * 35)
    
    print("\n📖 Paste your bedtime story below (press Enter twice when done):\n")
    
    # Read multi-line input
    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)
    
    story_text = "\n".join(lines).strip()
    
    if not story_text:
        print("\n❌ No story text provided. Exiting.")
        return
    
    # Speed selection
    print("\n🎙️  Choose speaking speed:")
    print("  1. Very slow (0.7x - extra calming)")
    print("  2. Slow (0.85x - RECOMMENDED for bedtime)")
    print("  3. Normal (1.0x)")
    
    speed_map = {
        '1': 0.7,
        '2': 0.85,
        '3': 1.0
    }
    
    choice = input("\nEnter your choice (1-3) [default: 2]: ").strip() or '2'
    speed = speed_map.get(choice, 0.85)
    
    # Filename
    default_filename = "bedtime_story.mp3"
    filename = input(f"\nOutput filename [default: {default_filename}]: ").strip() or default_filename
    
    # Generate audio
    audio_path = generate_audio_from_text(story_text, filename, speed)
    
    if audio_path:
        print(f"\n🔊 Success! Play the audio file to hear your bedtime story.")
        print(f"📁 Location: {audio_path}")
    else:
        print("\n❌ Audio generation failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
