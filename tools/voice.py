"""
Voice tools
===========
Speech-to-text via OpenAI Whisper (local, offline).
Text-to-speech via macOS `say` command (built-in, no API key needed).

Dependencies already on your machine:
  openai-whisper  — transcription
  sounddevice     — microphone recording
  numpy           — audio buffer
  scipy           — WAV file writing

Usage (standalone test):
  python tools/voice.py
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path


# ── Text-to-Speech ─────────────────────────────────────────────────────────────

def speak(text: str, voice: str = "Samantha") -> None:
    """
    Read text aloud using macOS built-in `say` command.
    Voice options: Samantha, Alex, Victoria, Karen, Daniel (UK), etc.
    On non-Mac, prints the text instead.
    """
    if sys.platform == "darwin":
        # Strip markdown symbols that sound weird when spoken
        clean = (text
                 .replace("**", "").replace("*", "").replace("#", "")
                 .replace("`", "").replace(">", "").replace("---", ""))
        subprocess.run(["say", "-v", voice, clean], check=False)
    else:
        print(f"[TTS] {text}")


# ── Speech-to-Text ─────────────────────────────────────────────────────────────

def record_and_transcribe(
    prompt_text: str = "Listening... press Enter to stop.",
    model_name: str = "base",
    samplerate: int = 16000,
) -> str:
    """
    Record audio from the default microphone until the user presses Enter,
    then transcribe with Whisper and return the transcript.

    model_name: "tiny", "base", "small", "medium", "large"
      - "base" is a good balance of speed and accuracy for English.
      - "tiny" is fastest but less accurate.
    """
    try:
        import numpy as np
        import sounddevice as sd
        from scipy.io.wavfile import write as wav_write
        import whisper
    except ImportError as e:
        return f"[voice] Missing dependency: {e}. Run: pip install openai-whisper sounddevice scipy numpy"

    print(f"\n🎙  {prompt_text}")

    # Record in a background thread; main thread waits for Enter
    recorded_chunks = []
    recording = [True]

    def audio_callback(indata, frames, time, status):
        if recording[0]:
            recorded_chunks.append(indata.copy())

    with sd.InputStream(samplerate=samplerate, channels=1, dtype="float32",
                        callback=audio_callback):
        input()   # blocks until user presses Enter

    recording[0] = False

    if not recorded_chunks:
        return ""

    import numpy as np
    audio = np.concatenate(recorded_chunks, axis=0).flatten()

    # Save to a temp WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        from scipy.io.wavfile import write as wav_write
        wav_write(tmp_path, samplerate, audio)

        print("  Transcribing...", end=" ", flush=True)
        model = whisper.load_model(model_name)
        result = model.transcribe(tmp_path, language="en", fp16=False)
        transcript = result["text"].strip()
        print(f"Done.\n  You said: \"{transcript}\"\n")
        return transcript

    finally:
        os.unlink(tmp_path)


# ── Standalone test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    speak("Voice mode is active. Press Enter to start speaking, then press Enter again to stop.")
    text = record_and_transcribe()
    if text:
        speak(f"I heard: {text}")
    else:
        speak("I didn't catch that.")
