import streamlit as st
from pytube import YouTube, Playlist
from tqdm import tqdm
import requests
import re
import os

def clean_filename(filename):
  # Replace invalid characters with underscores
  return re.sub(r'[\/:*?"<>|]', '_', filename)

def download_video(selected_stream, yt):
  # Get the user's Downloads folder path
  downloads_folder = os.path.expanduser("~" + os.sep + "Downloads")

  # Construct the full path to the output filename
  output_filename = os.path.join(downloads_folder, f"{clean_filename(yt.title)}_{selected_stream.resolution}.mp4")

  with requests.get(selected_stream.url, stream=True) as response:
    total_size = int(response.headers.get('content-length', 0))
    bytes_written = 0
    progress_bar = st.progress(0)

    with open(output_filename, "wb") as file:
      for data in response.iter_content(chunk_size=1024):
        file.write(data)
        bytes_written += len(data)
        progress = bytes_written / total_size
        progress_bar.progress(progress)

  return output_filename

# Title
st.title("YouTube Video Downloader")

# Sidebar
with st.sidebar:
  video_url = st.text_input("Enter YouTube video or playlist URL:")

  if video_url:
    # Check if it's a playlist URL
    if "list" in video_url:
      playlist = Playlist(video_url)
      st.write(f"Playlist: {playlist.title}")

      # Display videos in the playlist and create a checklist for download
      selected_videos = st.multiselect("Select videos to download:", playlist.video_urls)

      if st.button("Download Selected Videos"):
        # Download the selected videos to the default Downloads folder
        for video_url in selected_videos:
          yt = YouTube(video_url)
          selected_stream = yt.streams.get_highest_resolution()
          output_filename = download_video(selected_stream, yt)

          st.write(f"Download complete for {os.path.basename(output_filename)}")

    else:
      yt = YouTube(video_url)
      streams = yt.streams.filter(progressive=True)
      stream_list = [f"{stream.resolution} ({stream.mime_type})" for stream in streams]

      # Create a checklist to select streams
      selected_streams = st.multiselect("Select streams to download:", stream_list)

      if st.button("Download Video"):
        # Download the selected streams to the default Downloads folder
        for selected_stream_str in selected_streams:
          stream_resolution = selected_stream_str.split(" ")[0]
          selected_stream = next(s for s in streams if s.resolution == stream_resolution)
          output_filename = download_video(selected_stream, yt)

          st.write(f"Download complete for {os.path.basename(output_filename)}")

# Main screen
if 'yt' in locals() and "list" not in video_url:
  st.subheader(yt.title)

  # Adjust the width and height of the video
  width = 800
  height = 600

  # Use HTML to control the video size
  st.markdown(f'<video width="{width}" height="{height}" controls><source src="{yt.streams.get_highest_resolution().url}" type="video/mp4"></video>', unsafe_allow_html=True)
