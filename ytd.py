import os
import subprocess
import re
import tkinter as tk
from tkinter import ttk, messagebox

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

def download_video(link, folder, video_quality_key):
    """ Download video with selected quality """
    output = get_video_qualities(link)
    video_qualities, audio_qualities = parse_qualities(output)
    
    best_audio_quality = max(audio_qualities.keys(), key=lambda k: int(k))

    print('\n Video Qulity Key : '+ video_quality_key)

    command = f"yt-dlp -f '{video_quality_key}+{best_audio_quality}' -P {folder} '{link}'"
    print('\n Link : '+command)
    print("Download Started...")
    try:
        os.system(command)
        print(f"Downloaded in {folder}")
        messagebox.showinfo("Success", f"Downloaded in {folder}")
    except Exception as e:
        print(f"Error during download: {e}")
        messagebox.showerror("Error", f"Error during download: {e}")

def start_download():
    link = link_entry.get()
    folder = folder_entry.get().replace(" ", "_")
    selected_option = video_quality_var.get()

    if not link or not folder or not selected_option:
        messagebox.showerror("Error", "Please fill all fields")
        return

    if not os.path.exists(folder):
        os.makedirs(folder)

    video_quality_key = quality_mapping[selected_option]
    download_video(link, folder, video_quality_key)

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

app = tk.Tk()
app.title("YT-DLP Downloader")

link_label = tk.Label(app, text="Enter a playlist/video link:")
link_label.pack(pady=5)
link_entry = tk.Entry(app, width=50)
link_entry.pack(pady=5)

folder_label = tk.Label(app, text="Enter a name for the folder:")
folder_label.pack(pady=5)
folder_entry = tk.Entry(app, width=50)
folder_entry.pack(pady=5)

fetch_button = tk.Button(app, text="Fetch Qualities", command=fetch_qualities)
fetch_button.pack(pady=5)

video_quality_var = tk.StringVar()
quality_menu = ttk.Combobox(app, textvariable=video_quality_var, width=50)
quality_menu.pack(pady=5)

download_button = tk.Button(app, text="Download", command=start_download)
download_button.pack(pady=20)

app.mainloop()
