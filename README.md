# YouTube Grabber

A Python CLI tool for downloading YouTube videos from a playlist file with automatic progress tracking.

## Features

- Download YouTube videos at configurable quality (720p or 1080p)
- Automatic progress tracking - marks downloaded videos in the playlist file
- Smart resume - skips already downloaded videos
- Random delays between downloads to avoid rate limiting
- Colorized logging with detailed progress information
- Stops on any error to prevent data loss

## Installation

```bash
# Clone or navigate to the project directory
cd yt-grabber

# Install dependencies using uv
uv sync
```

## Configuration

Copy the example environment file and edit as needed:

```bash
cp .env.example .env
```

Available settings in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `VIDEO_QUALITY` | Video quality: `720` or `1080` | `1080` |
| `MIN_DELAY` | Minimum delay between downloads (seconds) | `1` |
| `MAX_DELAY` | Maximum delay between downloads (seconds) | `5` |
| `PLAYLIST_FILE` | Path to playlist file | `playlist.txt` |
| `DOWNLOAD_DIR` | Directory to save videos | `download` |

## Usage

### Basic Usage

Download videos from the default playlist file (`playlist.txt`):

```bash
uv run yt-grabber
```

### Custom Playlist File

Download from a different playlist file:

```bash
uv run yt-grabber /path/to/my-playlist.txt
```

## Playlist File Format

The playlist file should contain one YouTube URL per line:

```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

As videos are downloaded, they are automatically marked with `#`:

```
# https://www.youtube.com/watch?v=VIDEO_ID_1
# https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

Lines starting with `#` are skipped on subsequent runs, allowing you to resume interrupted downloads.

## How It Works

1. Reads URLs from the playlist file
2. Skips URLs already marked as downloaded (starting with `#`)
3. Downloads each video using yt-dlp at the configured quality
4. Marks successful downloads by prepending `#` to the URL
5. Waits a random delay before the next download
6. Stops immediately if any error occurs

## Requirements

- Python 3.14+
- uv package manager
- Dependencies: yt-dlp, pydantic-settings, loguru

## Error Handling

The program stops immediately if:
- A video fails to download
- The playlist file is not found
- Any unexpected error occurs

This prevents partial downloads and ensures data integrity.
