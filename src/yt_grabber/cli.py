"""Command-line interface for YouTube video downloader."""

import sys
from argparse import ArgumentParser
from pathlib import Path

from loguru import logger

from yt_grabber.config import Settings
from yt_grabber.downloader import VideoDownloader
from yt_grabber.playlist import PlaylistManager
from yt_grabber.playlist_extractor import PlaylistExtractor


def setup_logging() -> None:
    """Configure Loguru logging with colors."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
        level="INFO",
    )


def extract_playlist_command(args) -> None:
    """Extract URLs from a YouTube playlist."""
    try:
        output_path = Path(args.output)
        extractor = PlaylistExtractor()
        extractor.extract_urls(args.playlist_url, output_path)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


def download_command(args) -> None:
    """Download videos from a playlist file."""
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

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI application."""
    setup_logging()

    parser = ArgumentParser(
        description="YouTube video downloader and playlist extractor"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download command
    download_parser = subparsers.add_parser(
        "download",
        help="Download videos from a playlist file",
    )
    download_parser.add_argument(
        "playlist_file",
        nargs="?",
        help="Path to playlist file (default: from .env or playlist.txt)",
    )

    # Extract playlist command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract video URLs from a YouTube playlist",
    )
    extract_parser.add_argument(
        "playlist_url",
        help="YouTube playlist URL or playlist ID (e.g., PLJ49NV73ttruy7sqvirXaGL5CP-55cjgy)",
    )
    extract_parser.add_argument(
        "output",
        help="Output file path to save video URLs",
    )

    args = parser.parse_args()

    # Show help if no command specified
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Handle commands
    try:
        if args.command == "extract":
            extract_playlist_command(args)
        elif args.command == "download":
            download_command(args)

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
