import logging
from datetime import timedelta
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YoutubeTranscriber:
    """
    Production-level YouTube video transcriber.
    Attempts to fetch transcript using YouTubeTranscriptApi (captions).
    If captions are unavailable, returns a clear message (no model fallback).
    Handles errors and edge cases robustly.
    """
    MAX_DURATION_SECONDS = 45 * 60  # 45 minutes

    def __init__(self, url: str):
        """
        Args:
            url (str): YouTube video URL
        """
        self.url = url
        try:
            self.yt = YouTube(url)
        except Exception as e:
            logger.error(f"Error initializing YouTube object: {e}")
            raise ValueError(f"Invalid YouTube URL or network issue: {e}")

    def _get_video_duration(self) -> int:
        try:
            duration = self.yt.length
            logger.info(f"Video duration: {timedelta(seconds=duration)}")
            return duration
        except Exception as e:
            logger.error(f"Failed to get video duration: {e}")
            raise

    def _fetch_captions(self) -> str:
        video_id = self.yt.video_id
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = None
            for t in transcript_list:
                if t.language_code in ["en", "en-US"]:
                    transcript = t.fetch()
                    break
            if transcript is None:
                transcript = transcript_list.find_transcript([transcript_list[0].language_code]).fetch()
            full_text = " ".join([entry["text"] for entry in transcript])
            logger.info("Successfully fetched captions from YouTube API.")
            return full_text
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"Captions not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching captions: {e}")
            return None

    def get_transcription(self) -> str:
        """
        Orchestrates the transcription process:
          1. Checks video duration.
          2. Tries to fetch captions.
        Returns:
            str: The transcription text, or a message if unavailable.
        """
        try:
            duration = self._get_video_duration()
            if duration > self.MAX_DURATION_SECONDS:
                msg = f"Video longer than 45 minutes ({timedelta(seconds=duration)}), skipping transcription."
                logger.info(msg)
                return msg
            transcript = self._fetch_captions()
            if transcript:
                return transcript
            else:
                return "No transcript/captions available for this video."
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return f"Transcription failed: {e}"

# Example usage
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=Ks-_Mh1QhMc"
    transcriber = YoutubeTranscriber(url)
    result = transcriber.get_transcription()
    print(result)
