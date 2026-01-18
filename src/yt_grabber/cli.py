"""Command-line interface for YouTube video downloader."""

import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from yt_grabber.config import Settings
from yt_grabber.downloader import VideoDownloader
from yt_grabber.playlist import PlaylistManager
from yt_grabber.playlist_extractor import PlaylistExtractor

app = typer.Typer(help="YouTube video downloader and playlist extractor")


def setup_logging() -> None:
    """Configure Loguru logging with colors."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
        level="INFO",
    )


@app.command()
def extract(
    playlist_url: str = typer.Argument(
        ...,
        help="YouTube playlist URL or playlist ID (e.g., PLTj8zGbtGsjHQWtKYupS1CdZzrbbYKkoz)",
    ),
    output: str = typer.Argument(
        ...,
        help="Output file path to save video URLs",
    ),
) -> None:
    """Extract video URLs from a YouTube playlist."""
    setup_logging()

    try:
        output_path = Path(output)
        extractor = PlaylistExtractor()
        extractor.extract_urls(playlist_url, output_path)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise typer.Exit(1)


@app.command()
def download(
    playlist_file: Optional[str] = typer.Argument(
        None,
        help="Path to playlist file (default: from .env or playlist.txt)",
    ),
) -> None:
    """Download videos from a playlist file."""
    setup_logging()

    try:
        # Load settings
        settings = Settings()
        logger.info(f"Video quality: {settings.video_quality}p")
        logger.info(f"Delay range: {settings.min_delay}-{settings.max_delay}s")

        # Determine playlist file path
        if playlist_file:
            playlist_path = Path(playlist_file)
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
        raise typer.Exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise typer.Exit(1)


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        setup_logging()
        logger.warning("Interrupted by user")
        raise typer.Exit(130)


if __name__ == "__main__":
    main()
