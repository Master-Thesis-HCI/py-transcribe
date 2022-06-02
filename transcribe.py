"""
Tool to create a rough transcription draft for recorded speech (e.g. interviews).
"""
import speech_recognition as sr
import os
from pydub import AudioSegment
import librosa
import sys


LANGUAGE = "nl-NL"
CHUNK_SIZE = 30

input_file = sys.argv[1]
name = '.'.join(input_file.split('.')[:-1])
audio_file = "temp.wav"
transcript_file = name + ".md"

if os.path.exists(transcript_file):
    print(f"'{transcript_file}' already exists, remove or rename file existing flie first!")
    sys.exit()

if input_file.split('.')[-1] not in ["mp3", "MP3"]:
    print("Wrong file type")
    conversion_file = name + ".mp3"
    command = f"ffmpeg -i '{input_file}' '{conversion_file}' -y"
    print(f"Run:\n\t{command}\nand try again with the new file")
    sys.exit()

sound = AudioSegment.from_mp3(sys.argv[1])
sound.export(audio_file, format="wav")
audio_length = librosa.get_duration(filename=audio_file)

# use the audio file as the audio source                                        
r = sr.Recognizer()
transcription = []
with sr.AudioFile(audio_file) as source:
    transcription_length = 0
    while transcription_length < audio_length + CHUNK_SIZE:
        # The speech processing API doesn't allow large uploads, so we split the recording up
        audio = r.record(source, duration=CHUNK_SIZE)
        try:
            text = r.recognize_google(audio, language=LANGUAGE)
            transcription.append(text)
            print(transcription_length, "\t", text)
        except sr.UnknownValueError:
            print("--no transcript")
            pass
        except sr.RequestError:
            print("API error, lower chunk size", CHUNK_SIZE)
            break
        transcription_length += CHUNK_SIZE

os.remove(audio_file)

transcript = " ".join(transcription)
with open(transcript_file, 'w+') as f:
    f.write(transcript)

print(f"Saved transcript to {transcript_file}")
