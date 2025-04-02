from flask import Flask, jsonify, request
from flask_cors import CORS
from transcription_class import Video_Transcription
import os 

# Ensure the necessary directories exists
output_directory = "testing_medias"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    print(f"Created directory: {output_directory}")

app = Flask(__name__)
CORS(app)

transcriber = Video_Transcription()
aai_api_key = "c140112a971f4e408d1436cc5a612a40"

@app.route("/transcribe", methods=['POST'])
def video_transcription():
    try:
        # Get input file path
        media_path = request.form.get('file_path')
        video_lang = request.form.get('video_lang')
        output_video_path = request.form.get('output_path')
        
        # Check video main language.
        model = "best"
        if video_lang == "fa":
            model = "nano"
        else:
            model = "best"
        
        if not media_path or media_path is None:
            return jsonify({'error' : 'please identify the file you want to transcribe.'}), 400
        
        # Prcessing video
        print("*** processing video")
        extract_voice = transcriber.extract_voice_of_video(video_path=media_path, output_path="testing_medias/audio_path.mp3")
        denoise_voice = transcriber.noise_reduction(audio_path=extract_voice, output_path="testing_medias/denoised_voice.mp3")
        
        print("*** get transcription")
        # Get transcription of video.
        save_transcription_file = transcriber.get_transcription(audio_path=denoise_voice,
                                                    transcript_path=f"testing_medias/subtitle_{media_path.split('.mp4')[0]}.srt",
                                                    api_key=aai_api_key, language=video_lang, model=model)
        
        # Show subtitles on video frames using ffmpeg commands.
        print("*** display subtitle on video")
        displaying_subtitles = transcriber.overlay_subtitle_on_video(media_path, transcript_path=save_transcription_file,
                                                                    output_path=output_video_path)
        # print(displaying_subtitles)
        return jsonify({'status' : "successful !",
                        'output_file_saved' : displaying_subtitles}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"error" : "an Unexpected error found."}), 500


if __name__ == '__main__':
    app.run()