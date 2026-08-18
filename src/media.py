import wave
from pathlib import Path

import orjson
import yt_dlp
from vosk import KaldiRecognizer, Model


class PathTrackerPP(yt_dlp.postprocessor.PostProcessor):
    """Custom post-processor to capture both the final video and audio paths."""

    def __init__(self):
        super().__init__()
        self.video_path = None
        self.audio_path = None

    def run(self, information):
        # 1. Grab the original downloaded video path
        self.video_path = information.get("filepath")

        # 2. Grab the final extracted audio path if it exists
        # yt-dlp populates '__files_to_move' with post-processed files
        files_to_move = information.get("__files_to_move", {})
        if files_to_move:
            # The destination audio path is the value in this dictionary
            self.audio_path = next(iter(files_to_move.values()))

        return [], information


def download_social_video(video_url, output_folder="downloads"):
    """
    Downloads a video and extracts its audio using custom ydl_opts.

    :param video_url: The URL of the social media video.
    :param output_folder: Directory where the files will be saved.
    :return: A dictionary containing 'video' and 'audio' pathlib.Path objects.
    """

    ydl_opts = {
        # 1. Download best video and best audio streams
        "format": "bestvideo[vcodec!=none]+bestaudio[acodec!=none]/best",
        "merge_output_format": "mp4",
        # Name format: saves file as "Title (Platform) [Video_ID].ext"
        "outtmpl": f"{output_folder}/[%(id)s].%(ext)s",
        # Overwrite existing files if they have the same name
        "no_overwrites": False,
        # A standard user-agent helps bypass bot-detection algorithms on FB/Insta
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
        # Suppress excessive terminal outputs, but keep error messages
        "quiet": False,
        "no_warnings": False,
        # 2. Extract WAV audio from the downloaded video
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        # 3. Pass FFmpeg arguments to resample audio to 16000 Hz and convert to 16-bit PCM
        "postprocessor_args": [
            "-ar",
            "16000",  # Set audio sample rate to 16 kHz
            "-ac",
            "1",  # Set to 1 channel (mono) - standard for Whisper/speech models
        ],
        # 3. CRITICAL: Prevent yt-dlp from deleting the MP4 video after audio extraction
        "keepvideo": True,
        "ffmpeg_location": r"C:\ffmpeg\bin",
    }

    try:
        print(f"Starting download pipeline for: {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Instantiate and attach our path tracker
            path_tracker = PathTrackerPP()
            ydl.add_post_processor(path_tracker)

            # Execute download & extraction
            ydl.download([video_url])

            # Build and return the Path object dictionary
            result = {
                "video": Path(path_tracker.video_path)
                if path_tracker.video_path
                else None,
                "audio": Path(path_tracker.audio_path)
                if path_tracker.audio_path
                else None,
            }
            if result["video"]:
                return Path(result["video"]).with_suffix(".wav")

    except TypeError as e:
        print(f"Error during execution: {e}")

    return None


def transcribe_wav(file_path: str) -> str:
    """Return the full transcript of a 16 kHz mono PCM WAV file."""
    # Initialize model (change path if needed)
    model = Model("Models/vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)

    transcript_parts = []

    with wave.open(file_path, "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if not data:
                break
            if rec.AcceptWaveform(data):
                # Append intermediate results
                transcript_parts.append(orjson.loads(rec.Result()).get("text", ""))

    # Append final result
    transcript_parts.append(orjson.loads(rec.FinalResult()).get("text", ""))

    # Join all parts and return
    return " ".join(part for part in transcript_parts if part)
