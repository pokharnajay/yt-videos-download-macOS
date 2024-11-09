import os
import subprocess
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread

def get_video_qualities(link):
    """ Get available video and audio qualities for the given link. """
    command = f"yt-dlp -F {link}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def parse_qualities(output):
    """ Parse the qualities from yt-dlp output. """
    video_qualities = {}
    audio_qualities = {}

    lines = output.splitlines()
    for line in lines:
        if re.search(r'^\d+\s+mp4', line):
            parts = line.split()
            fmt_id = parts[0]
            quality = parts[2] + ' - ' + parts[3] + 'fps'
            video_qualities[fmt_id] = quality
        elif re.search(r'^\d+\s+m4a', line):
            parts = line.split()
            fmt_id = parts[0]
            quality = "audio"
            audio_qualities[fmt_id] = quality

    return video_qualities, audio_qualities

def download_video(link, folder, video_quality_key, filename):
    """ Download video with selected quality and filename and show progress. """
    try:
        download_button.config(state=tk.DISABLED)  # Disable the download button

        output = get_video_qualities(link)
        video_qualities, audio_qualities = parse_qualities(output)
        best_audio_quality = max(audio_qualities.keys(), key=lambda k: int(k))

        command = f"yt-dlp -f {video_quality_key}+{best_audio_quality} -o \"{folder}/{filename}.%(ext)s\" {link}"

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in iter(process.stdout.readline, ''):
            if '[download]' in line:
                match = re.search(r'(\d+\.\d+%)\s+of\s+.*?ETA\s+(.*)', line)
                if match:
                    percentage = match.group(1)
                    eta = match.group(2)
                    progress_label.config(text=f"Progress: {percentage} - ETA: {eta}")
                    app.update()

        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            messagebox.showinfo("Success", f"Downloaded in {folder}")
        else:
            messagebox.showerror("Error", "Download failed")
    except Exception as e:
        messagebox.showerror("Error", f"Error during download: {e}")
    finally:
        download_button.config(state=tk.NORMAL)  # Re-enable the download button

def start_download_thread():
    thread = Thread(target=start_download)
    thread.start()

def start_download():
    link = link_entry.get()
    selected_option = video_quality_var.get()
    filename = filename_entry.get()

    if not link or not selected_folder or not selected_option or not filename:
        messagebox.showerror("Error", "Please fill all fields")
        return

    video_quality_key = quality_mapping[selected_option]
    download_video(link, selected_folder, video_quality_key, filename)

def fetch_qualities():
    global quality_mapping
    link = link_entry.get()
    if not link:
        messagebox.showerror("Error", "Please enter a link")
        return

    output = get_video_qualities(link)
    video_qualities, _ = parse_qualities(output)

    quality_mapping = {f"{fmt_id}: {quality}": fmt_id for fmt_id, quality in video_qualities.items()}
    quality_options = list(quality_mapping.keys())
    quality_menu['values'] = quality_options

def select_folder():
    global selected_folder
    selected_folder = filedialog.askdirectory()
    if selected_folder:
        folder_label.config(text=f"Selected Folder: {selected_folder}")

app = tk.Tk()
app.title("YT-DLP Downloader")

link_label = tk.Label(app, text="Enter a playlist/video link:")
link_label.pack(pady=5)
link_entry = tk.Entry(app, width=50)
link_entry.pack(pady=5)

folder_button = tk.Button(app, text="Select Download Folder", command=select_folder)
folder_button.pack(pady=5)

folder_label = tk.Label(app, text="No folder selected")
folder_label.pack(pady=5)

filename_label = tk.Label(app, text="Enter a name for the download file:")
filename_label.pack(pady=5)
filename_entry = tk.Entry(app, width=50)
filename_entry.pack(pady=5)

fetch_button = tk.Button(app, text="Fetch Qualities", command=fetch_qualities)
fetch_button.pack(pady=5)

video_quality_var = tk.StringVar()
quality_menu = ttk.Combobox(app, textvariable=video_quality_var, width=50)
quality_menu.pack(pady=5)

download_button = tk.Button(app, text="Download", command=start_download_thread)
download_button.pack(pady=20)

progress_label = tk.Label(app, text="Progress: Not started")
progress_label.pack(pady=5)

selected_folder = ""

app.mainloop()
