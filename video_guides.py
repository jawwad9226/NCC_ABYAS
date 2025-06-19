import os
import json
import streamlit as st
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import re

# Assuming utils_youtube.py is in the same directory or Python path
from utils_youtube import fetch_youtube_videos

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
@dataclass
class Video:
    """Represents a video in the NCC video library."""
    id: str
    title: str
    url: str
    description: str
    duration: str
    category: str
    thumbnail: str
    tags: List[str] = field(default_factory=list)

def extract_youtube_id(url: str) -> Optional[str]:
    """Extracts YouTube video ID from various URL formats or if URL is an ID itself."""
    if not url:
        return None
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    # Check if the 'url' itself is a valid YouTube ID
    if re.fullmatch(r'[a-zA-Z0-9_-]{11}', url):
        return url
    return None

class VideoLibrary:
    """Manages the NCC video library."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.videos: List[Video] = []
        self.categories: List[str] = []
        self.version: str = "1.0"
        self.api_key = api_key
        self._load_data()
    
    def _load_data(self) -> None:
        """
        Load video data from the JSON file.
        If an API key is provided and a video is identified as a YouTube video,
        it attempts to fetch/enrich its metadata using the YouTube Data API.
        """
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, "data", "videos.json")
            
            if not os.path.exists(file_path):
                st.error(f"Video data file not found: {file_path}")
                self.videos = []
                self.categories = []
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.version = data.get("version", "1.0")
            
            # Process videos from all categories
            for category, video_list in data.items():
                if category == "version":
                    continue
                    
                if not isinstance(video_list, list):
                    st.warning(f"Expected a list of videos for category '{category}', got {type(video_list)}. Skipping.")
                    continue

                temp_videos_pending_api_fetch: List[Video] = []

                for idx, video_data in enumerate(video_list):
                    try:
                        json_video_id = video_data.get("id")
                        json_url = video_data.get("url", "")
                        
                        # Try to extract YouTube ID from URL first, then from JSON's 'id' field
                        youtube_id = extract_youtube_id(json_url) or extract_youtube_id(json_video_id or "")

                        if self.api_key and youtube_id:
                            # Prepare a shell for API fetching. ID will be the YouTube ID.
                            video_shell = Video(
                                id=youtube_id,
                                title=video_data.get("title", "Loading title..."),
                                url=f"https://www.youtube.com/watch?v={youtube_id}", # Canonical URL
                                description=video_data.get("description", "Loading description..."),
                                duration=video_data.get("duration", "N/A"),
                                category=category,
                                thumbnail=video_data.get("thumbnail", ""), # Keep manual thumbnail as initial
                                tags=video_data.get("tags", [])[:] # Copy list
                            )
                            temp_videos_pending_api_fetch.append(video_shell)
                        else:
                            # Not a YouTube video, or no API key; load directly from JSON
                            # Use JSON ID, or YouTube ID (if extracted but API not used), or generate.
                            final_id = json_video_id or youtube_id or f"manual_{category.lower().replace(' ','_')}_{idx}"
                            manual_video = Video(
                                id=final_id,
                                title=video_data.get("title", "Untitled Video"),
                                url=json_url,
                                description=video_data.get("description", "No description available."),
                                duration=video_data.get("duration", "N/A"),
                                category=category,
                                thumbnail=video_data.get("thumbnail", ""),
                                tags=video_data.get("tags", [])[:] # Copy list
                            )
                            if manual_video.url:
                                self.videos.append(manual_video)
                    except Exception as e:
                        st.error(f"Error processing individual video data in category '{category}': {e}. Video data: {video_data}")

                # Batch fetch from YouTube API for current category's videos
                if self.api_key and temp_videos_pending_api_fetch:
                    ids_to_fetch = [v.id for v in temp_videos_pending_api_fetch]
                    if ids_to_fetch:
                        try:
                            youtube_videos_details = fetch_youtube_videos(ids_to_fetch, self.api_key)
                            details_map = {detail['id']: detail for detail in youtube_videos_details}

                            for video_shell in temp_videos_pending_api_fetch:
                                # Find the original JSON data for this shell to access overrides
                                original_json_data = next((vd for vd in video_list if (extract_youtube_id(vd.get("url","")) == video_shell.id or vd.get("id") == video_shell.id)), {})

                                yt_details = details_map.get(video_shell.id)
                                if yt_details:
                                    video_shell.title = original_json_data.get("title_override") or yt_details['title']
                                    video_shell.description = original_json_data.get("description_override") or yt_details['description']
                                    video_shell.duration = self._format_youtube_duration(yt_details['duration'])
                                    # Use manually specified thumbnail (already in shell) if present, else API's
                                    video_shell.thumbnail = video_shell.thumbnail or yt_details['thumbnail']
                                    # Merge tags: JSON tags (already in shell) + API tags (unique)
                                    video_shell.tags = list(set(video_shell.tags + yt_details.get('tags', [])))
                                else:
                                    st.warning(f"Could not fetch details for YouTube video ID: {video_shell.id} in category '{category}'. Using data from videos.json or placeholders.")
                                
                                if video_shell.url:
                                    self.videos.append(video_shell)
                        except Exception as e:
                            st.error(f"Error fetching video details from YouTube API: {e}")
                            # Add shells as they are if API fails
                            for video_shell in temp_videos_pending_api_fetch:
                                if video_shell.url:
                                    self.videos.append(video_shell)
            
            # Update categories
            self.categories = sorted(list(set(v.category for v in self.videos)))
            
        except FileNotFoundError:
            # Already handled at the top of the try block for file_path
            pass
        except json.JSONDecodeError as e:
            st.error(f"Error parsing video data: {e}")
        except Exception as e:
            st.error(f"Unexpected error loading video data: {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")

    def _format_youtube_duration(self, duration_str: str) -> str:
        """Formats ISO 8601 duration string from YouTube API to HH:MM:SS or MM:SS."""
        if not duration_str or not duration_str.startswith("PT"): return duration_str # Not a YouTube duration format or empty
        duration_str = duration_str[2:] # Remove PT
        hours, minutes, seconds = 0, 0, 0
        if 'H' in duration_str: parts = duration_str.split('H'); hours = int(parts[0]); duration_str = parts[1] if len(parts) > 1 else ""
        if 'M' in duration_str: parts = duration_str.split('M'); minutes = int(parts[0]); duration_str = parts[1] if len(parts) > 1 else ""
        if 'S' in duration_str: seconds = int(duration_str.replace('S', ''))
        if hours > 0: return f"{hours:01}:{minutes:02}:{seconds:02}"
        return f"{minutes:02}:{seconds:02}" if minutes > 0 else f"00:{seconds:02}"

    def get_videos(self, category: str = None, search_query: str = None) -> List[Video]:
        """Get videos filtered by category and search query."""
        videos = self.videos
        
        if category and category != "All":
            videos = [v for v in videos if v.category == category]
            
        if search_query:
            search_lower = search_query.lower()
            videos = [
                v for v in videos
                if (search_lower in v.title.lower() or
                    search_lower in v.description.lower() or
                    any(search_lower in tag.lower() for tag in v.tags))
            ]
            
        return videos

def video_guides():
    """Display the video guides section."""
    st.write("Explore a collection of helpful videos related to NCC topics.")
    
    if not YOUTUBE_API_KEY:
        st.info(
            "Optional: YOUTUBE_API_KEY environment variable is not set. "
            "YouTube video details (like latest titles, descriptions, durations) "
            "will not be fetched automatically. The app will rely solely on `videos.json`."
        )

    # Initialize video library
    if 'video_lib' not in st.session_state:
        st.session_state.video_lib = VideoLibrary(api_key=YOUTUBE_API_KEY)
    
    video_lib: VideoLibrary = st.session_state.video_lib
    
    # Check for version mismatch
    if video_lib.version != "1.0":
        st.warning(
            f"Video data file version mismatch. Expected '1.0', but found '{video_lib.version}'. "
            "Functionality might be limited or incorrect. Please update your data/videos.json."
        )
    
    # Category selection
    selected_category = st.selectbox(
        "Choose a Video Category:",
        ["All"] + video_lib.categories,
        key="video_category"
    )
    
    # Search functionality
    search_query = st.text_input(
        "Search Videos:",
        placeholder="e.g., 'parade', 'map reading', 'first aid'",
        key="video_search"
    )
    
    # Get filtered videos
    videos = video_lib.get_videos(selected_category, search_query)
    
    # Display videos
    if not videos:
        st.info("No videos found matching your criteria.")
    else:
        cols = st.columns(2)
        for i, video in enumerate(videos):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"#### {video.title}") # Using H4 for slightly smaller title

                    # Display thumbnail
                    if video.thumbnail:
                        try:
                            if video.thumbnail.startswith("file:///"):
                                # Handle local file paths (assuming Unix-like paths from your error)
                                # For Windows, path might be like "file:///C:/..."
                                # and replace would be video.thumbnail.replace("file:///", "")
                                local_path = video.thumbnail.replace("file:///", "/")
                                if os.path.exists(local_path):
                                    st.image(local_path, use_container_width=True)
                                else:
                                    st.warning(f"Local thumbnail not found: {local_path}")
                                    st.image("https://via.placeholder.com/320x180.png?text=Thumbnail+Not+Found", use_container_width=True)
                            else:
                                # Handle web URLs
                                st.image(video.thumbnail, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading thumbnail for '{video.title}': {e}")
                            st.image("https://via.placeholder.com/320x180.png?text=Error+Loading+Thumb", use_container_width=True)
                    else:
                        # Placeholder if no thumbnail is specified
                        st.image(
                            "https://via.placeholder.com/320x180.png?text=No+Thumbnail",
                            use_container_width=True
                        )
                    
                    details_cols = st.columns([1,1])
                    with details_cols[0]:
                        st.caption(f"Duration: {video.duration}")
                    with details_cols[1]:
                        st.caption(f"Category: {video.category}")

                    # Show description with expander
                    if video.description:
                        desc = video.description
                        if len(desc) > 100:
                            with st.expander("Description"):
                                st.write(desc)
                        else:
                            st.write(desc)
                        
                    # Show tags if available
                    # if video.tags: # Tags display removed as per user request
                    #     st.write("**Tags:** " + ", ".join(f"`{tag}`" for tag in video.tags))
                
                    # Play button
                    if st.button("▶️ Play Video", key=f"play_{video.id}"):
                        st.video(video.url)
                    
                    st.markdown("---")
    
    # Offline mode note
    st.markdown("---")
    st.markdown("""
    **Note on Offline Mode:**
    For true offline access, videos would need to be downloaded and stored locally.
    The `st.video()` function can play local files if their paths are provided.
    Currently, this feature fetches online video details if a YouTube API key is set.
    """)
