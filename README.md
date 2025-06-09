# YouTube Video Downloader GUI

A simple desktop application to download YouTube videos with a graphical user interface.

## Features

*   Paste a YouTube video URL.
*   Fetch available video qualities.
*   Select preferred video quality.
*   Choose a local folder to save the downloaded video.
*   Downloads video, best audio, and English subtitles (if available).
*   Merges video and audio into an MP4 file.
*   Displays download progress.

## Prerequisites

*   Python 3.x
*   FFmpeg: `yt-dlp` requires FFmpeg for merging formats. Please download it from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) and ensure it's added to your system's PATH or is in the same directory as the application.

## How to Run

1.  **Clone the repository (or download the files):**
    ```bash
    git clone https://github.com/kiarashfallah/youtube-downloader.git
    cd youtube-downloader-gui
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the application:**
    ```bash
    python youtube_downloader_app.py
    ```

