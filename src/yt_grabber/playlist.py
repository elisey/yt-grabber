"""Playlist file management for tracking downloaded videos."""

from pathlib import Path
from typing import List

from loguru import logger


class PlaylistManager:
    """Manages reading and updating playlist files with download tracking."""

    DOWNLOADED_MARKER = "#"
    HEADER_MARKER = ":"

    def __init__(self, playlist_path: Path):
        """Initialize playlist manager.

        Args:
            playlist_path: Path to the playlist file
        """
        self.playlist_path = playlist_path

    def read_urls(self) -> List[str]:
        """Read undownloaded URLs from the playlist file.

        Returns:
            List of URLs that are not marked as downloaded

        Raises:
            FileNotFoundError: If playlist file does not exist
        """
        if not self.playlist_path.exists():
            raise FileNotFoundError(f"Playlist file not found: {self.playlist_path}")

        urls = []
        with open(self.playlist_path, "r") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Skip header lines (marked with :)
                if line.startswith(self.HEADER_MARKER):
                    logger.debug(f"Line {line_num}: Header line, skipping")
                    continue

                # Skip already downloaded URLs (marked with #)
                if line.startswith(self.DOWNLOADED_MARKER):
                    logger.debug(f"Line {line_num}: Already downloaded, skipping")
                    continue

                urls.append(line)
                logger.debug(f"Line {line_num}: Added URL to queue")

        logger.info(f"Found {len(urls)} URLs to download")
        return urls

    def mark_as_downloaded(self, url: str) -> None:
        """Mark a URL as downloaded by prepending # to its line.

        Args:
            url: The URL to mark as downloaded

        Raises:
            ValueError: If URL is not found in the playlist file
        """
        # Read all lines from the file
        with open(self.playlist_path, "r") as f:
            lines = f.readlines()

        # Find and mark the URL
        url_found = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == url:
                lines[i] = f"{self.DOWNLOADED_MARKER} {line}"
                url_found = True
                logger.debug(f"Marked URL as downloaded at line {i + 1}")
                break

        if not url_found:
            raise ValueError(f"URL not found in playlist: {url}")

        # Write back to file
        with open(self.playlist_path, "w") as f:
            f.writelines(lines)

        logger.success(f"Updated playlist file: {self.playlist_path}")
