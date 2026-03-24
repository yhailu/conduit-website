"""Generate the call demo audio using edge-tts (free Microsoft TTS)."""
import asyncio
import edge_tts
import os
import subprocess
import json

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Agent = warm, professional female voice
# Caller = natural female voice (different one)
AGENT_VOICE = "en-US-JennyNeural"      # Warm, professional
CALLER_VOICE = "en-US-AriaNeural"       # Natural, slightly different tone

SCRIPT = [
    ("agent", "Thank you for calling Sterling Family Law. This is Olivia, how can I help you today?"),
    ("caller", "Hi, I need to speak with an attorney about a divorce."),
    ("agent", "Of course. I'm sorry you're going through this, and I'm here to help. I'll just need to ask a few quick questions to match you with the right attorney. Can I get your name?"),
    ("caller", "Sarah Mitchell."),
    ("agent", "Thank you, Sarah. Is this a new matter, or do you have an existing case with us?"),
    ("caller", "It's new. My husband and I just decided to separate."),
    ("agent", "I understand. Our family law team specializes in exactly this. Are there any children involved?"),
    ("caller", "Yes, we have two kids, ages 8 and 11."),
    ("agent", "Thank you for sharing that, Sarah. That helps us prepare. I have availability this Thursday at 2pm or Friday at 10am for a free 30-minute consultation with Attorney Davis, who specializes in custody and divorce cases. Which works better?"),
    ("caller", "Thursday at 2 works."),
    ("agent", "You're all set. Thursday at 2pm with Attorney Davis. I'll send a confirmation to your email along with a brief intake form. Is there anything else I can help with today?"),
    ("caller", "No, that's great. Thank you."),
    ("agent", "You're welcome, Sarah. Take care, and we'll see you Thursday. Goodbye."),
]

async def generate_line(speaker, text, index):
    voice = AGENT_VOICE if speaker == "agent" else CALLER_VOICE
    filename = os.path.join(OUTPUT_DIR, f"line_{index:02d}_{speaker}.mp3")
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    print(f"  Generated: {filename}")
    return filename

async def main():
    print("Generating individual lines...")
    files = []
    for i, (speaker, text) in enumerate(SCRIPT):
        f = await generate_line(speaker, text, i)
        files.append(f)
    
    # Create a silence file (0.8 seconds) for gaps between lines
    silence_file = os.path.join(OUTPUT_DIR, "silence.mp3")
    
    # Use ffmpeg if available to concatenate, otherwise just list files
    # First check if ffmpeg exists
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        has_ffmpeg = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        has_ffmpeg = False
    
    if has_ffmpeg:
        # Generate silence
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", "0.8", "-q:a", "9", silence_file
        ], capture_output=True)
        
        # Build concat list
        concat_file = os.path.join(OUTPUT_DIR, "concat.txt")
        with open(concat_file, "w") as f:
            for i, audio_file in enumerate(files):
                f.write(f"file '{audio_file}'\n")
                if i < len(files) - 1:
                    f.write(f"file '{silence_file}'\n")
        
        output = os.path.join(OUTPUT_DIR, "call-demo.mp3")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file, "-acodec", "libmp3lame", "-q:a", "2", output
        ], capture_output=True)
        
        print(f"\nFinal audio: {output}")
        print(f"Size: {os.path.getsize(output)} bytes")
        
        # Cleanup individual files
        for f in files:
            os.remove(f)
        os.remove(silence_file)
        os.remove(concat_file)
    else:
        print("\nffmpeg not found - individual files saved. Concatenate manually or install ffmpeg.")
        print("Files:", files)

asyncio.run(main())
