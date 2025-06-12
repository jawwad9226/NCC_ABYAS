
import os
import json
import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass

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
    tags: List[str]

class VideoLibrary:
    """Manages the NCC video library."""
    
    def __init__(self):
        self.videos: List[Video] = []
        self.categories: List[str] = []
        self.version: str = "1.0"
        self._load_data()
    
    def _load_data(self) -> None:
        """Load video data from the JSON file."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, "data", "videos.json")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.version = data.get("version", "1.0")
            
            # Process videos from all categories
            for category, video_list in data.items():
                if category == "version":
                    continue
                    
                for video_data in video_list:
                    try:
                        video = Video(
                            id=video_data.get("id", str(len(self.videos))),
                            title=video_data.get("title", "Untitled Video"),
                            url=video_data.get("url", ""),
                            description=video_data.get("description", "No description available."),
                            duration=video_data.get("duration", "N/A"),
                            category=category,
                            thumbnail=video_data.get("thumbnail", ""),
                            tags=video_data.get("tags", [])
                        )
                        if video.url:  # Only add if URL is present
                            self.videos.append(video)
                    except Exception as e:
                        st.error(f"Error processing video data: {e}")
            
            # Update categories
            self.categories = sorted(list(set(v.category for v in self.videos)))
            
        except FileNotFoundError:
            st.error("Video data file not found. Please ensure 'data/videos.json' exists.")
        except json.JSONDecodeError as e:
            st.error(f"Error parsing video data: {e}")
        except Exception as e:
            st.error(f"Unexpected error loading video data: {e}")
    
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
    st.header("🎥 NCC Video Guides")
    st.write("Explore a collection of helpful videos related to NCC topics.")
    
    # Initialize video library
    if 'video_lib' not in st.session_state:
        st.session_state.video_lib = VideoLibrary()
    
    video_lib = st.session_state.video_lib
    
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
                    st.markdown(f"### {video.title}")
                    
                    # Display thumbnail if available, otherwise show a placeholder
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if video.thumbnail:
                            st.image(
                                video.thumbnail,
                                width=160,
                                use_column_width=True,
                                output_format="PNG"
                            )
                        else:
                            st.image(
                                "https://via.placeholder.com/160x90?text=No+Thumbnail",
                                width=160,
                                use_column_width=True
                            )
                    
                    with col2:
                        st.write(f"**Duration:** {video.duration}")
                        st.write(f"**Category:** {video.category}")
                        
                        # Show description with expander if it's long
                        desc = video.description
                        if len(desc) > 100:
                            with st.expander("Description"):
                                st.write(desc)
                        else:
                            st.write(desc)
                        
                        # Show tags if available
                        if video.tags:
                            st.write("**Tags:** " + ", ".join(f"`{tag}`" for tag in video.tags))
                    
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
    """)
