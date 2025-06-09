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
    git clone <repository_url>
    cd <repository_directory>
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

## How to Build an Executable (Optional)

You can package this application into a standalone executable using PyInstaller.

1.  **Ensure you have FFmpeg.** For the executable to work correctly, users will still need FFmpeg. You might consider bundling FFmpeg with your distribution or instructing users to place it in the same directory as the executable.
2.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
3.  **Build the executable:**
    *   For a single-file executable (may have slower startup):
        ```bash
        pyinstaller --name YouTubeDownloader --onefile --windowed --add-data "customtkinter:customtkinter" youtube_downloader_app.py
        ```
    *   For a one-folder bundle (faster startup):
        ```bash
        pyinstaller --name YouTubeDownloader --onedir --windowed --add-data "customtkinter:customtkinter" youtube_downloader_app.py
        ```
    The `--add-data "customtkinter:customtkinter"` part is often necessary for CustomTkinter applications. You might need to adjust paths depending on your environment.
    The executable will be found in the `dist` folder.

## Notes

*   This application uses `yt-dlp` for downloading. Ensure you comply with YouTube's terms of service and copyright laws in your region.
*   Automatic subtitle download is set to English (`en`). This can be modified in the script.