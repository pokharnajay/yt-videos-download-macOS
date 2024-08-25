import os
import subprocess
import re

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
            quality = parts[2] + ' - ' +parts[3] + 'fps'
            video_qualities[fmt_id] = quality
        elif re.search(r'^\d+\s+m4a', line):
            parts = line.split()
            fmt_id = parts[0]
            quality = "audio"
            audio_qualities[fmt_id] = quality

    return video_qualities, audio_qualities

def display_qualities(qualities, quality_type):
    """ Display available qualities for selection. """
    print(f"Available {quality_type} qualities:")
    for fmt_id, quality in qualities.items():
        print(f"{fmt_id}: {quality}")

def select_quality(qualities, quality_type):
    """ Allow the user to select one quality. """
    while True:
        fmt_id = input(f"Enter the format ID for the {quality_type} quality you want to download: ")
        if fmt_id in qualities:
            return fmt_id
        else:
            print("Invalid format ID. Please try again.")

def download(link):
    folder = input("Enter a name for the folder: ").replace(" ", "_")

    if os.path.exists(folder):
        print(f"Using existing folder: {folder}")
    else:
        os.makedirs(folder)
        print(f"Created folder: {folder}")

    print("Fetching available video and audio qualities...")
    output = get_video_qualities(link)
    video_qualities, audio_qualities = parse_qualities(output)

    display_qualities(video_qualities, "video")
    selected_video_quality = select_quality(video_qualities, "video")

    # Select the best audio quality (highest format ID)
    best_audio_quality = max(audio_qualities.keys(), key=lambda k: int(k))

    command = f"yt-dlp -f '{selected_video_quality}+{best_audio_quality}' -P {folder} '{link}'"

    print("Download Started...")
    try:
        os.system(command)
        print(f"Downloaded in {folder}")
    except Exception as e:
        print(f"Error during download: {e}")

if __name__ == "__main__":
    link = input("Enter a playlist/video link: ")
    download(link)
