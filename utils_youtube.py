import os
from typing import List, Dict
from googleapiclient.discovery import build

def fetch_youtube_videos(video_ids: List[str], api_key: str) -> List[Dict]:
    """
    Fetch video details from YouTube Data API for the given list of video IDs.
    Args:
        video_ids: List of YouTube video IDs.
        api_key: Your YouTube Data API key.
    Returns:
        List of dicts with video metadata.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(
        part='snippet,contentDetails',
        id=','.join(video_ids)
    )
    response = request.execute()
    videos = []
    for item in response.get('items', []):
        videos.append({
            'id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'duration': item['contentDetails']['duration'],
            'tags': item['snippet'].get('tags', [])
        })
    return videos
