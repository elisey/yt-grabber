"""YouTube video downloader using yt-dlp."""

import random
import time
from pathlib import Path
from typing import List

import yt_dlp
from loguru import logger

from yt_grabber.config import Settings
from yt_grabber.playlist import PlaylistManager


class VideoDownloader:
    """Downloads YouTube videos using yt-dlp."""

    def __init__(self, settings: Settings):
        """Initialize the video downloader.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.download_dir = Path(settings.download_dir)

        # Create download directory if it doesn't exist
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _get_ydl_opts(self) -> dict:
        """Get yt-dlp options based on settings.

        Returns:
            Dictionary of yt-dlp options
        """
        # Format selection based on quality setting
        if self.settings.video_quality == "1080":
            format_string = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        else:  # 720
            format_string = "bestvideo[height<=720]+bestaudio/best[height<=720]"

        return {
            "format": format_string,
            "outtmpl": str(self.download_dir / "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": False,
            "no_warnings": False,
            "progress_hooks": [],
        }

    def download_video(self, url: str) -> None:
        """Download a single video from URL.

        Args:
            url: YouTube video URL

        Raises:
            Exception: If download fails
        """
        logger.info(f"Starting download: {url}")
        start_time = time.time()

        ydl_opts = self._get_ydl_opts()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Extract video information
                video_id = info.get("id", "Unknown")
                video_title = info.get("title", "Unknown")
                filename = ydl.prepare_filename(info)

                # Calculate download time
                download_time = time.time() - start_time

                # Log statistics
                logger.success(f"Downloaded: {video_title}")
                logger.info(f"Statistics:")
                logger.info(f"  Video ID: {video_id}")
                logger.info(f"  File: {Path(filename).name}")
                logger.info(f"  Download time: {download_time:.2f}s")

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            raise

    def _random_delay(self) -> None:
        """Wait for a random delay between min_delay and max_delay."""
        if self.settings.max_delay <= 0:
            return

        delay = random.uniform(self.settings.min_delay, self.settings.max_delay)
        logger.info(f"Waiting {delay:.2f} seconds before next download...")
        time.sleep(delay)

    def download_playlist(self, playlist_manager: PlaylistManager) -> None:
        """Download all videos from a playlist file.

        Args:
            playlist_manager: PlaylistManager instance

        Raises:
            Exception: If any download fails (stops entire process)
        """
        urls = playlist_manager.read_urls()

        if not urls:
            logger.warning("No URLs to download")
            return

        logger.info(f"Starting download of {len(urls)} videos")

        for idx, url in enumerate(urls, start=1):
            logger.info(f"Progress: {idx}/{len(urls)}")

            try:
                # Download the video
                self.download_video(url)

                # Mark as downloaded
                playlist_manager.mark_as_downloaded(url)

                # Add delay before next download (except for last video)
                if idx < len(urls):
                    self._random_delay()

            except Exception as e:
                logger.error(f"Error downloading video {idx}/{len(urls)}: {e}")
                logger.error("Stopping download process due to error")
                raise

        logger.success(f"All {len(urls)} videos downloaded successfully!")
