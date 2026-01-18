"""Base extractor class for YouTube content."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import yt_dlp
from loguru import logger


class BaseExtractor(ABC):
    """Base class for extracting URLs from YouTube content."""

    @abstractmethod
    def normalize_url(self, url_input: str) -> str:
        """Normalize input to full YouTube URL.

        Args:
            url_input: URL or ID

        Returns:
            Full YouTube URL
        """
        pass

    def _extract_video_ids(self, url: str) -> List[str]:
        """Extract video IDs from YouTube URL.

        Args:
            url: YouTube URL (playlist or channel)

        Returns:
            List of video IDs

        Raises:
            ValueError: If no videos found
            Exception: If extraction fails
        """
        logger.info(f"Extracting URLs from: {url}")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "force_generic_extractor": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if "entries" not in info:
                    raise ValueError("No videos found")

                # Extract video IDs
                video_ids = []
                for entry in info["entries"]:
                    if entry:
                        video_id = entry.get("id")
                        if video_id:
                            video_ids.append(video_id)

                if not video_ids:
                    raise ValueError("No valid video IDs found")

                return video_ids

        except Exception as e:
            logger.error(f"Failed to extract: {e}")
            raise

    def extract_urls(self, url_input: str, output_file: Path) -> None:
        """Extract all video URLs and save to file.

        Args:
            url_input: YouTube URL or ID
            output_file: Path to save the extracted URLs

        Raises:
            Exception: If extraction fails
        """
        url = self.normalize_url(url_input)
        video_ids = self._extract_video_ids(url)

        # Convert IDs to URLs
        urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]

        # Subclasses can transform the URL list
        urls = self.transform_urls(urls)

        # Save to file
        with open(output_file, "w") as f:
            for url in urls:
                f.write(f"{url}\n")

        # Log statistics
        logger.success(f"Extraction completed")
        logger.info(f"Statistics:")
        logger.info(f"  Videos found: {len(urls)}")
        logger.info(f"  Saved to: {output_file}")

    def transform_urls(self, urls: List[str]) -> List[str]:
        """Transform URL list before saving (e.g., reverse order).

        Args:
            urls: List of video URLs

        Returns:
            Transformed list of URLs
        """
        return urls
