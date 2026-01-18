"""Extract video URLs from YouTube playlists."""

from pathlib import Path

import yt_dlp
from loguru import logger


class PlaylistExtractor:
    """Extracts video URLs from YouTube playlists."""

    def _normalize_playlist_url(self, playlist_input: str) -> str:
        """Normalize playlist input to full URL.

        Args:
            playlist_input: Playlist URL or ID

        Returns:
            Full YouTube playlist URL
        """
        # If it's already a full URL, return as is
        if playlist_input.startswith("http://") or playlist_input.startswith("https://"):
            return playlist_input

        # If it's just an ID, construct the URL
        return f"https://www.youtube.com/playlist?list={playlist_input}"

    def extract_urls(self, playlist_input: str, output_file: Path) -> None:
        """Extract all video URLs from a playlist and save to file.

        Args:
            playlist_input: YouTube playlist URL or playlist ID
            output_file: Path to save the extracted URLs

        Raises:
            Exception: If extraction fails
        """
        playlist_url = self._normalize_playlist_url(playlist_input)
        logger.info(f"Extracting URLs from playlist: {playlist_url}")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "force_generic_extractor": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)

                if "entries" not in info:
                    raise ValueError("No videos found in playlist")

                # Extract video URLs
                urls = []
                for entry in info["entries"]:
                    if entry:
                        video_id = entry.get("id")
                        if video_id:
                            url = f"https://www.youtube.com/watch?v={video_id}"
                            urls.append(url)

                if not urls:
                    raise ValueError("No valid video URLs found")

                # Save to file
                with open(output_file, "w") as f:
                    for url in urls:
                        f.write(f"{url}\n")

                # Log statistics
                logger.success(f"Playlist extraction completed")
                logger.info(f"Statistics:")
                logger.info(f"  Videos found: {len(urls)}")
                logger.info(f"  Saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to extract playlist: {e}")
            raise
