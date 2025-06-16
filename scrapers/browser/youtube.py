import logging
from datetime import timedelta
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Uncomment if using openai-whisper; make sure to install it and its dependencies.
# import whisper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeTranscriber:
    MAX_DURATION_SECONDS = 45 * 60  # 45 minutes

    def __init__(self, url: str):
        """
        Initialize the transcriber with a YouTube URL.
        """
        self.url = url
        try:
            self.yt = YouTube(url)
        except Exception as e:
            logger.error(f"Error initializing YouTube object: {e}")
            raise

    def _get_video_duration(self) -> int:
        """
        Return video duration in seconds.
        """
        duration = self.yt.length  # in seconds
        logger.info(f"Video duration: {timedelta(seconds=duration)}")
        return duration

    def _fetch_captions(self) -> str:
        """
        Try to fetch available captions using the YouTube Transcript API.
        Returns the concatenated transcript if captions available.
        """
        video_id = self.yt.video_id
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # Try to find a transcript that is in English or auto-generated
            transcript = None
            for t in transcript_list:
                if t.language_code in ["en", "en-US"]:
                    transcript = t.fetch()
                    break
            if transcript is None:
                # Fallback to first available transcript
                transcript = transcript_list.find_transcript([transcript_list[0].language_code]).fetch()

            # Concatenate the text parts
            full_text = " ".join([entry["text"] for entry in transcript])
            logger.info("Successfully fetched captions from YouTube API.")
            return full_text
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"Captions not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching captions: {e}")
            raise

    def _transcribe_with_model(self) -> str:
        """
        Transcribe the video using a transcription model (e.g., Whisper).
        For production, you would load a pre-trained model and transcribe the video.
        This is a placeholder for a more advanced transcription mechanism.
        """
        try:
            logger.info("Falling back on model-based transcription with Whisper...")
            # Download the video’s audio stream
            audio_stream = self.yt.streams.filter(only_audio=True).first()
            audio_file = audio_stream.download(filename_prefix="audio_")
            logger.info(f"Downloaded audio to {audio_file}")

            # Uncomment below if using whisper, adjust model loading as needed.
            # model = whisper.load_model("base")
            # result = model.transcribe(audio_file)
            # transcription = result.get("text", "")

            # Placeholder transcription to simulate model transcription
            transcription = "Transcription from model would appear here."
            return transcription
        except Exception as e:
            logger.error(f"Model transcription failed: {e}")
            raise

    def get_transcription(self) -> str:
        """
        Orchestrates the transcription process:
          1. Check if video duration exceeds MAX_DURATION_SECONDS.
          2. Try to fetch captions via YouTubeTranscriptApi.
          3. If captions are not available, use the transcription model.
        Returns the transcription text.
        """
        duration = self._get_video_duration()
        if duration > self.MAX_DURATION_SECONDS:
            msg = f"Video longer than 45 minutes ({timedelta(seconds=duration)}), skipping transcription."
            logger.info(msg)
            return msg

        try:
            transcription = self._fetch_captions()
            return transcription
        except Exception:
            logger.info("Using transcription model as captions are unavailable.")
            return self._transcribe_with_model()


# Example usage:
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=YourVideoID"
    transcriber = YouTubeTranscriber(url)
    result = transcriber.get_transcription()
    print(result)