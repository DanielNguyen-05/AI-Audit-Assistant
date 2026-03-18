# src/youtube_scraper.py
import os
import re
import yt_dlp
from googleapiclient.discovery import build

def extract_playlist_id(url):
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def get_playlist_videos(playlist_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    videos = []
    request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
    while request:
        response = request.execute()
        for item in response.get("items", []):
            videos.append({
                "video_id": item["snippet"]["resourceId"]["videoId"],
                "title": item["snippet"]["title"]
            })
        request = youtube.playlistItems().list_next(request, response)
    return videos

def download_subtitles(video_id, output_dir="data/raw"):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['vi', 'en'],
        'subtitlesformat': 'vtt',
        'outtmpl': os.path.join(output_dir, f'{video_id}.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'sleep_interval_requests': 1,
        'sleep_interval': 2
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"Đã xử lý tải sub cho video: {video_id}")