from moviepy.video.io.VideoFileClip import VideoFileClip
import assemblyai as aai
import pysrt
from deep_translator import GoogleTranslator
import subprocess
import noisereduce as nr
import librosa
import soundfile as sf


class Video_Transcription:
    def __init__(self):
        self.en_translator = GoogleTranslator(source='auto', target='en')
        self.fa_translator = GoogleTranslator(source='auto', target='fa')

    # Extract voice from video
    def extract_voice_of_video(self, video_path : str, output_path : str) -> str:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_path)
        return output_path
    
    # Reduce noise from audio
    def noise_reduction(self, audio_path : str, output_path : str) -> str:
        data, samplerate = librosa.load(audio_path)
        reduced_noise = nr.reduce_noise(y=data, sr=samplerate)
        sf.write(output_path, reduced_noise, samplerate)
        return output_path
    
    # Transcribe the audio and save the transcript
    def get_transcription(self, audio_path : str, transcript_path : str,
                          api_key : str, language : str, model : str) -> None:    
        aai.settings.api_key = api_key
        config = aai.TranscriptionConfig(language_code=language, speech_model=model)
        transcriber = aai.Transcriber(config=config)    
        transcript = transcriber.transcribe(audio_path)
        export_subtitle = transcript.export_subtitles_srt()
        with open(transcript_path, 'w') as f:
            f.write(export_subtitle)
        return transcript_path
    
    # Translate the transcript bilingually and save the new transcript
    def bilingual_translate_transcript(self, transcript_path : str, main_language : str, font_color : str) -> str:
        subs = pysrt.open(transcript_path)
        if main_language == "fa":
            for sub in subs:
                sub.text = f"<font color={font_color}>{sub.text}\n{self.en_translator.translate(sub.text)}</font>"
        else:
            for sub in subs:
                sub.text = f"<font color={font_color}>{sub.text}\n{self.fa_translator.translate(sub.text)}</font>"
        subs.save(transcript_path)
        return transcript_path
    
    # Translate transcription to only one lanuage.
    def translate_tanscription_one_lang(self, transcript_path : str, output_path : str, main_lang : str, font_color : str) -> str:
        subs = pysrt.open(transcript_path)
        if main_lang == "fa":
            for sub_f in subs:
                sub_f.text = f"<font color={font_color}>{self.en_translator.translate(sub_f.text)}</font>"
            subs.save(output_path)
        else:
            for sub_e in subs:
                sub_e.text = f"<font color={font_color}>{self.fa_translator.translate(sub_e.text)}</font>"
            subs.save(output_path)
        return output_path
    
    # Overlay subtitle on video
    def overlay_subtitle_on_video(self, video_path : str, 
                                  transcript_path : str, output_path : str) -> None:
        # Terminal command:
        # ffmpeg -i media/david_malan.mp4 -vf "subtitles=media/david_malan.srt:charenc=UTF-8" -c:a copy output2.mp4
        # Define input and output file paths
        
        # Construct the FFmpeg command
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles={transcript_path}",
            "-c:a", "copy",
            output_path
        ]
        subprocess.run(command, check=True)
        
        return output_path


# Here's a test code to use the class.

# class_obj = Video_Transcription()
# audio_path = class_obj.extract_voice_of_video(video_path="./david_malan.mp4", output_path="./testing_medias/david_malan_voice.mp3")
# print(audio_path)
# denoised_voice = class_obj.noise_reduction(audio_path=audio_path, output_path="./audioes/game_develop_nr.mp3")
# get_transcript = class_obj.get_transcription(audio_path=denoised_voice, tr    anscript_path="./media/game_develop.srt",
#                                              api_key="c140112a971f4e408d1436cc5a612a40", language="en", model="best")
# translations = class_obj.bilingual_translate_transcript(get_transcript, main_language="en", font_color="red")
# translations = class_obj.translate_tanscription_one_lang(get_transcript, "./media/game_develop_fa.srt",
#                                                          main_lang="en", font_color="white")

# add_subtitles = class_obj.overlay_subtitle_on_video(video_path="./media/game_develop.mp4", 
#                                                     transcript_path="./media/game_develop_fa.srt", 
#                                                     output_path="./media/game_develop_subtitled_fa.mp4")
# print(translations)