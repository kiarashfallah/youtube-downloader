# YouTube Downloader Application

import yt_dlp
import os
import logging
import customtkinter
from tkinter import filedialog
import threading # For running downloads in a separate thread

# Logger class for yt-dlp
class MyLogger:
    def __init__(self, app_logger_func=None):
        self.app_logger_func = app_logger_func

    def debug(self, msg):
        if "yt-dlp|" in msg: # Filter specific yt-dlp debug messages
            pass
        elif self.app_logger_func:
            self.app_logger_func(f"DEBUG: {msg}") # Send to app's status
        else:
            print(f"DEBUG: {msg}")

    def warning(self, msg):
        if self.app_logger_func:
            self.app_logger_func(f"WARNING: {msg}")
        else:
            print(f"WARNING: {msg}")

    def error(self, msg):
        if self.app_logger_func:
            self.app_logger_func(f"ERROR: {msg}")
        else:
            print(f"ERROR: {msg}")

# Original progress_hook (console-based) - can be kept for non-GUI use or removed
# def progress_hook(d):
#     if d['status'] == 'downloading':
#         print(f"CONSOLE: Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
#     if d['status'] == 'finished':
#         print(f"CONSOLE: Done downloading, now converting or merging...")

# yt-dlp functions
def get_formats_core(url, logger_instance):
    """Core logic for fetching formats, matching Colab's filtering logic."""
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'logger': logger_instance,
        'noplaylist': True,
    }
    formats_list = []
    video_info = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            video_info['title'] = info_dict.get('title', 'video')
            video_info['duration'] = info_dict.get('duration_string', 'N/A')

            seen_res = set()
            for f in sorted(info_dict.get('formats', []), key=lambda x: x.get('height') or 0, reverse=True):
                height = f.get('height')
                if f.get('vcodec') != 'none' and height and height not in seen_res:
                    label = f"{height}p - {f.get('ext')}"
                    formats_list.append({'label': label, 'id': f.get('format_id'), 'ext': f.get('ext')})
                    seen_res.add(height)
                if len(formats_list) >= 10:
                    break

            return formats_list, video_info, None
        except yt_dlp.utils.DownloadError as e:
            return [], {"title": "Error"}, str(e)
        except Exception as e:
            return [], {"title": "Error"}, f"An unexpected error occurred: {e}"

def download_video_core(url, selected_format_id, video_title, download_path, logger_instance, progress_hook_gui=None):
    """Core logic for downloading video, matching Colab's download behavior."""
    os.makedirs(download_path, exist_ok=True)

    sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_', '[', ']') else '_' for c in video_title)
    sanitized_title = "_".join(sanitized_title.split())

    output_template = os.path.join(download_path, f"{sanitized_title}.%(ext)s")

    ydl_opts = {
        'format': f"{selected_format_id}+bestaudio",
        'outtmpl': output_template,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'logger': logger_instance,
        'progress_hooks': [progress_hook_gui] if progress_hook_gui else [],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"Download of '{sanitized_title}' complete. Saved in '{download_path}'", None
    except yt_dlp.utils.DownloadError as e:
        return None, str(e)
    except Exception as e:
        return None, f"An unexpected error occurred during download: {e}"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Video Downloader")
        self.geometry("700x600") # Increased height for progress bar

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)

        # --- UI Elements ---
        # URL Input
        self.url_input_label = customtkinter.CTkLabel(self, text="YouTube URL:")
        self.url_input_label.grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        self.url_input = customtkinter.CTkEntry(self, placeholder_text="https://www.youtube.com/watch?v=...", width=350)
        self.url_input.grid(row=0, column=1, padx=10, pady=(10,5), sticky="ew")
        self.fetch_button = customtkinter.CTkButton(self, text="Fetch Qualities", command=self.fetch_qualities_gui)
        self.fetch_button.grid(row=0, column=2, padx=10, pady=(10,5))

        # Quality Selection
        self.quality_label = customtkinter.CTkLabel(self, text="Select Quality:")
        self.quality_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.quality_dropdown = customtkinter.CTkOptionMenu(self, values=["-- Fetch qualities first --"], command=self.on_quality_selected)
        self.quality_dropdown.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        # Download Directory
        self.dir_label = customtkinter.CTkLabel(self, text="Download Folder:")
        self.dir_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.selected_dir_label = customtkinter.CTkLabel(self, text="No folder selected", wraplength=300, anchor="w")
        self.selected_dir_label.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.browse_button = customtkinter.CTkButton(self, text="Browse", command=self.browse_directory_gui)
        self.browse_button.grid(row=2, column=2, padx=10, pady=5)

        # Download Button
        self.download_button = customtkinter.CTkButton(self, text="Download", command=self.download_video_gui, state="disabled")
        self.download_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Progress Bar (added in this step)
        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0) # Initial value
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=(5,5), sticky="ew")

        # Status Label
        self.status_label = customtkinter.CTkLabel(self, text="Welcome! Enter a URL to begin.", wraplength=650, anchor="w", justify="left")
        self.status_label.grid(row=5, column=0, columnspan=3, padx=10, pady=(5,10), sticky="ew")

        # --- App State Variables ---
        self.formats_cache = [] # Stores dicts: {'label': str, 'id': str, 'ext': str}
        self.current_video_info = {} # Stores {'title': str, 'duration': str}
        self.download_directory = "" # Stores selected download path
        self.selected_format_id = None # Stores the chosen format ID from dropdown

        # Initialize MyLogger with a method to update the status label
        self.gui_logger = MyLogger(app_logger_func=self.log_to_status_bar)


    def log_to_status_bar(self, message):
        """Helper to log messages to the status bar, ensuring UI updates are on the main thread."""
        def _update_status():
            self.status_label.configure(text=message)
        self.after(0, _update_status) # Schedule the update on the Tkinter main loop

    def fetch_qualities_gui(self):
        url = self.url_input.get()
        if not url:
            self.log_to_status_bar("Please enter a YouTube URL.")
            return

        self.log_to_status_bar("Fetching qualities...")
        self.download_button.configure(state="disabled")
        self.quality_dropdown.configure(values=["-- Fetching... --"])
        self.quality_dropdown.set("-- Fetching... --")
        self.progress_bar.set(0)

        # Run in a separate thread to keep UI responsive
        threading.Thread(target=self._fetch_qualities_thread, args=(url,), daemon=True).start()

    def _fetch_qualities_thread(self, url):
        formats, info, error_msg = get_formats_core(url, self.gui_logger)

        def _update_ui():
            if error_msg:
                self.log_to_status_bar(f"Error fetching: {error_msg}")
                self.quality_dropdown.configure(values=["-- Error --"])
                self.quality_dropdown.set("-- Error --")
                self.current_video_info = {}
                self.formats_cache = []
            elif formats:
                self.current_video_info = info
                self.formats_cache = formats

                dropdown_values = [f['label'] for f in self.formats_cache]
                self.quality_dropdown.configure(values=dropdown_values)
                if dropdown_values:
                    self.quality_dropdown.set(dropdown_values[0]) # Select first by default
                    self.on_quality_selected(dropdown_values[0]) # Trigger selection logic
                else:
                    self.quality_dropdown.set("-- No compatible formats --") # Should not happen if formats is not empty

                self.log_to_status_bar(f"Qualities loaded for: {self.current_video_info.get('title', 'Unknown Video')}")
                self.check_download_ready()
            else:
                self.log_to_status_bar("No formats found or video is unavailable.")
                self.quality_dropdown.configure(values=["-- No formats found --"])
                self.quality_dropdown.set("-- No formats found --")
                self.current_video_info = {}
                self.formats_cache = []

        self.after(0, _update_ui) # Schedule UI updates on the main thread

    def on_quality_selected(self, selected_label):
        # Find the format ID for the selected label
        self.selected_format_id = None
        for fmt in self.formats_cache:
            if fmt['label'] == selected_label:
                self.selected_format_id = fmt['id']
                break
        self.check_download_ready()


    def browse_directory_gui(self):
        directory = filedialog.askdirectory()
        if directory: # If a directory is selected
            self.download_directory = directory
            self.selected_dir_label.configure(text=self.download_directory)
            self.log_to_status_bar(f"Download folder selected: {self.download_directory}")
        else: # If dialog is cancelled
            self.log_to_status_bar("Directory selection cancelled.")
        self.check_download_ready()

    def check_download_ready(self):
        if self.download_directory and self.selected_format_id and self.url_input.get():
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")

    def download_video_gui(self):
        url = self.url_input.get()
        if not url:
            self.log_to_status_bar("Error: YouTube URL is missing.")
            return

        if not self.selected_format_id:
            self.log_to_status_bar("Error: Please select a quality.")
            return

        if not self.download_directory:
            self.log_to_status_bar("Error: Please select a download folder.")
            return

        video_title = self.current_video_info.get("title", "youtube_video")

        self.log_to_status_bar(f"Preparing to download '{video_title}'...")
        self.download_button.configure(state="disabled") # Disable while downloading
        self.fetch_button.configure(state="disabled") # Disable while downloading
        self.progress_bar.set(0) # Reset progress bar

        # Run download in a separate thread
        threading.Thread(target=self._download_video_thread,
                         args=(url, self.selected_format_id, video_title, self.download_directory),
                         daemon=True).start()

    def _download_video_thread(self, url, format_id, title, path):
        result_msg, error_msg = download_video_core(url, format_id, title, path,
                                                self.gui_logger, self.update_progress_gui)
        def _update_ui():
            if error_msg:
                self.log_to_status_bar(f"Download Error: {error_msg}")
            else:
                self.log_to_status_bar(result_msg)
                self.progress_bar.set(1) # Mark as complete

            self.download_button.configure(state="normal") # Re-enable download button
            self.fetch_button.configure(state="normal") # Re-enable fetch button
            self.check_download_ready() # Re-check state, though likely fine.

        self.after(0, _update_ui)


    def update_progress_gui(self, d):
        """Hook for yt-dlp to update GUI elements."""
        def _update():
            if d['status'] == 'downloading':
                self.fetch_button.configure(state="disabled") # Ensure fetch is disabled
                self.download_button.configure(state="disabled") # Ensure download is disabled

                total_bytes_estimate = d.get('total_bytes_estimate')
                total_bytes = d.get('total_bytes')
                downloaded_bytes = d.get('downloaded_bytes')

                if total_bytes_estimate: # Use estimate if available
                    percent = (downloaded_bytes / total_bytes_estimate)
                    self.progress_bar.set(percent)
                    self.status_label.configure(text=f"Downloading: {d.get('_percent_str', 'N/A')} of ~{d.get('_total_bytes_estimate_str', 'N/A')} at {d.get('_speed_str', 'N/A')}")
                elif total_bytes : # Fallback to total_bytes if no estimate
                    percent = (downloaded_bytes / total_bytes)
                    self.progress_bar.set(percent)
                    self.status_label.configure(text=f"Downloading: {d.get('_percent_str', 'N/A')} of {d.get('_total_bytes_str', 'N/A')} at {d.get('_speed_str', 'N/A')}")
                else: # If no size info, show generic message
                    self.status_label.configure(text=f"Downloading... (Speed: {d.get('_speed_str', 'N/A')})")
                    self.progress_bar.set(0) # Or use an indeterminate mode if available and desired

            elif d['status'] == 'finished':
                self.progress_bar.set(1) # Mark as complete before final message
                self.status_label.configure(text="Download finished. Processing/Merging...")
            elif d['status'] == 'error':
                self.status_label.configure(text=f"Error during download: {d.get('error', 'Unknown error')}")
                self.download_button.configure(state="normal")
                self.fetch_button.configure(state="normal")

        self.after(0, _update) # Schedule UI updates on the main thread


if __name__ == '__main__':
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    app = App()
    app.mainloop()
