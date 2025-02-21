import speech_recognition as sr

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    full_transcription = ""

    with sr.AudioFile(file_path) as source:
        recognizer.adjust_for_ambient_noise(source)  # Improve accuracy
        total_duration = int(source.DURATION)  # Get total audio length
        chunk_size = 10  # Process in 10-second chunks

        for i in range(0, total_duration, chunk_size):
            audio = recognizer.record(source, offset=i, duration=chunk_size)
            try:
                text = recognizer.recognize_google(audio)
                full_transcription += text + " "  # Append transcribed text
            except sr.UnknownValueError:
                full_transcription += "[Unrecognized Audio] "
            except sr.RequestError:
                return "Error: Could not connect to Google API"

    return full_transcription.strip()

# Example usage:
if __name__ == "__main__":
    file_path = "uploads/sample.wav"  # Update with your actual file path
    transcription = transcribe_audio(file_path)
    print("Transcription:\n", transcription)

