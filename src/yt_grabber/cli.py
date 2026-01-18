"""Command-line interface for YouTube video downloader."""

import sys
from argparse import ArgumentParser
from pathlib import Path

from loguru import logger

from yt_grabber.config import Settings
from yt_grabber.downloader import VideoDownloader
from yt_grabber.playlist import PlaylistManager


def setup_logging() -> None:
    """Configure Loguru logging with colors."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
        level="INFO",
    )


def main() -> None:
    """Main entry point for the CLI application."""
    setup_logging()

    parser = ArgumentParser(
        description="Download YouTube videos from a playlist file"
    )
    parser.add_argument(
        "playlist_file",
        nargs="?",
        help="Path to playlist file (default: from .env or playlist.txt)",
    )

    args = parser.parse_args()

    try:
        # Load settings
        settings = Settings()
        logger.info(f"Video quality: {settings.video_quality}p")
        logger.info(f"Delay range: {settings.min_delay}-{settings.max_delay}s")

        # Determine playlist file path
        if args.playlist_file:
            playlist_path = Path(args.playlist_file)
            logger.info(f"Using playlist file from argument: {playlist_path}")
        else:
            playlist_path = Path(settings.playlist_file)
            logger.info(f"Using default playlist file: {playlist_path}")

        # Initialize components
        playlist_manager = PlaylistManager(playlist_path)
        downloader = VideoDownloader(settings)

        # Start downloading
        logger.info(f"Download directory: {settings.download_dir}")
        downloader.download_playlist(playlist_manager)

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Download interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
