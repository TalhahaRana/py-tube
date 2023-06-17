# python -m streamlit run app.py

import time
import os
import streamlit as st
import pytube
import requests
from PIL import Image
from io import BytesIO


def download_video(url, outputpath, resolution, output_format):
    youtube = pytube.YouTube(url)
    if output_format == "mp3":
        audio_stream = youtube.streams.get_audio_only()
        audio_stream.download(outputpath)
        # Convert the downloaded audio file to MP3
        video_file_path = os.path.join(outputpath, audio_stream.default_filename)
        mp3_file_path = os.path.splitext(video_file_path)[0] + ".mp3"
        os.rename(video_file_path, mp3_file_path)
    else:
        if resolution is not None:
            video_stream = youtube.streams.get_by_resolution(resolution)
        else:
            video_stream = youtube.streams.get_highest_resolution()
        if video_stream:
            video_stream.download(outputpath)
        else:
            raise ValueError("No video streams available for download.")


def get_video_thumbnail(url):
    thumbnail_url = pytube.YouTube(url).thumbnail_url
    # Download thumbnail image
    response = requests.get(thumbnail_url)
    thumbnail_image = Image.open(BytesIO(response.content))
    return thumbnail_image


# Set page configuration
st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon=":arrow_down:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Page title and description
st.title("YouTube Video Downloader")
st.markdown("Enter the YouTube video URL and select the output format and quality. Then click the *Download* button to save the video in your preferred format.")

# Input fields
video_url = st.text_input("YouTube Video URL")
if video_url:
    try:
        video = pytube.YouTube(video_url)
        video_id = pytube.extract.video_id(video_url)
        st.write("Video Title")
        st.success(video.title)
        st.image(get_video_thumbnail(video_id), width=200)
    except pytube.exceptions.PytubeError:
        pass  # Handle the exception silently without displaying an error message

# Output format selection
output_format = st.selectbox("Select Output Format", ["mp4", "mp3"])

# Video quality selection
if output_format == "mp4":
    if video_url:
        video = pytube.YouTube(video_url)
        available_resolutions = [stream.resolution for stream in video.streams.filter(file_extension="mp4")]
        selected_resolution = st.selectbox("Select Video Quality", available_resolutions)

# Download
if st.button("Download"):
    if video_url:
        try:
            with st.spinner("Downloading video..."):
                download_path = os.path.expanduser("~\Downloads")
                if output_format == "mp4":
                    download_video(video_url, download_path, selected_resolution, output_format)
                else:
                    download_video(video_url, download_path, None, output_format)
                time.sleep(2)
                st.success("Video downloaded successfully!")
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.warning("Please enter a valid YouTube video URL.")