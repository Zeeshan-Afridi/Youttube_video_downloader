import streamlit as st
from pytube import YouTube, Playlist
from tqdm import tqdm
import requests
import re
import os

def clean_filename(filename):
    # Replace invalid characters with underscores
    return re.sub(r'[\/:*?"<>|]', '_', filename)

# Title
st.title("YouTube Video Downloader")

# Sidebar
with st.sidebar:
    video_url = st.text_input("Enter YouTube video or playlist URL:")

    if video_url:
        if "list" in video_url:  # Check if it's a playlist URL
            playlist = Playlist(video_url)
            st.write(f"Playlist: {playlist.title}")

            # Display videos in the playlist and create a checklist for download
            selected_videos = st.multiselect("Select videos to download:", playlist.video_urls)
 
            if st.button("Download Selected Videos"):

                st.write(f"Downloading selected videos")

                for video_url in selected_videos:
                    yt = YouTube(video_url)
                    streams = yt.streams.filter(progressive=True)
                    selected_stream = streams.get_highest_resolution()

                    # Use tqdm to track download progress
                    clean_title = clean_filename(yt.title)
                    output_filename = clean_title

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

                    st.write(f"Download complete for {clean_title}. Saved to {output_filename}")

        else:  # Single video URL
            yt = YouTube(video_url)
            streams = yt.streams.filter(progressive=True)
            stream_list = [f"{stream.resolution} ({stream.mime_type})" for stream in streams]

            # Create a checklist to select streams
            selected_streams = st.multiselect("Select streams to download:", stream_list)

            # Create a file uploader for selecting the download folder
            download_folder = st.file_uploader("Select download folder:", type=["folder"])

            if st.button("Download Video") and download_folder is not None:
                download_path = download_folder.name

                for stream in selected_streams:
                    stream_resolution = stream.split(" ")[0]
                    selected_stream = next(s for s in streams if s.resolution == stream_resolution)
                    st.write(f"Downloading {selected_stream.resolution} video to {download_path}...")

                    # Use tqdm to track download progress
                    clean_title = clean_filename(yt.title)
                    output_filename = os.path.join(download_path, f"{clean_title}_{selected_stream.resolution}.mp4")

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

                    st.write(f"Download complete for {selected_stream.resolution} video. Saved to {output_filename}")

# Main screen
if 'yt' in locals() and "list" not in video_url:
    st.subheader(yt.title)
    # Adjust the width and height of the video
    width = 800
    height = 600
    # Use HTML to control the video size
    st.markdown(f'<video width="{width}" height="{height}" controls><source src="{yt.streams.get_highest_resolution().url}" type="video/mp4"></video>', unsafe_allow_html=True)
