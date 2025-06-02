import streamlit as st
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Video:
    title: str
    url: str
    description: str = ""
    duration: str = ""

# NCC Video Library
NCC_VIDEOS: Dict[str, List[Video]] = {
    "Drill": [
        Video(
            "NCC Drill Training Basics",
            "https://www.youtube.com/embed/45a6V4bSe0A",
            "Learn the fundamentals of NCC drill training including basic commands and formations.",
            "12:45"
        ),
        Video(
            "Advanced Drill Commands",
            "https://www.youtube.com/embed/8Q-4ckqIedU",
            "Advanced drill commands and ceremonial movements for senior cadets.",
            "15:30"
        ),
        Video(
            "NCC Parade Commands",
            "https://www.youtube.com/embed/3qMkZ-s5vYQ",
            "Complete guide to NCC parade commands and execution.",
            "18:15"
        )
    ],
    "Weapon Training": [
        Video(
            "Handling .22 Rifle in NCC",
            "https://www.youtube.com/embed/XD3Ha0Ah7Fs",
            "Proper handling and safety procedures for .22 rifles in NCC training.",
            "18:22"
        ),
        Video(
            "Weapon Safety Protocols",
            "https://www.youtube.com/embed/9X_ViIPA-Gc",
            "Essential safety measures and protocols for weapon handling.",
            "10:15"
        ),
        Video(
            "Rifle Assembly & Disassembly",
            "https://www.youtube.com/embed/7YHjGXkYw7k",
            "Step-by-step guide to assembling and disassembling standard issue rifles.",
            "14:30"
        )
    ],
    "Map Reading": [
        Video(
            "Basics of Map and Compass",
            "https://www.youtube.com/embed/F9UxuFgdnK0",
            "Introduction to map reading and compass use for navigation.",
            "14:30"
        ),
        Video(
            "Advanced Navigation Techniques",
            "https://www.youtube.com/embed/6v2L2zZ0y_M",
            "Advanced land navigation skills for NCC cadets.",
            "16:45"
        ),
        Video(
            "Topographic Map Reading",
            "https://www.youtube.com/embed/4jfoYM67W4o",
            "How to read and interpret topographic maps.",
            "12:20"
        )
    ],
    "First Aid": [
        Video(
            "NCC First Aid Demo",
            "https://www.youtube.com/embed/ntEZWYKnQQk",
            "Demonstration of basic first aid techniques for NCC cadets.",
            "22:10"
        ),
        Video(
            "CPR Training",
            "https://www.youtube.com/embed/gz0M9cfFNq0",
            "Complete CPR training for emergency situations.",
            "08:45"
        ),
        Video(
            "First Aid for Fractures",
            "https://www.youtube.com/embed/8DJ45ekU7h8",
            "How to handle and provide first aid for fractures.",
            "11:30"
        )
    ],
    "Leadership": [
        Video(
            "Leadership in NCC",
            "https://www.youtube.com/embed/XrfF4jFq53E",
            "Developing leadership skills through NCC training programs.",
            "16:45"
        ),
        Video(
            "Team Building Exercises",
            "https://www.youtube.com/embed/6kZxJtVbBgY",
            "Effective team building activities for cadets.",
            "14:20"
        ),
        Video(
            "Public Speaking for Leaders",
            "https://www.youtube.com/embed/bGBamf6Nk54",
            "Improving public speaking skills for NCC cadet leaders.",
            "19:15"
        )
    ],
    "Disaster Management": [
        Video(
            "Fire Drill & Earthquake Tips",
            "https://www.youtube.com/embed/1xRCa6Gs1LQ",
            "Emergency response training for fire drills and earthquakes.",
            "19:30"
        ),
        Video(
            "Flood Safety Measures",
            "https://www.youtube.com/embed/M5uYCWVfuPQ",
            "Safety procedures and response during flood situations.",
            "12:45"
        ),
        Video(
            "Disaster Preparedness",
            "https://www.youtube.com/embed/JF9FO5HRcJQ",
            "Comprehensive guide to disaster preparedness and response.",
            "15:20"
        )
    ]
}

def display_video_guides():
    """Display the main video guides interface."""
    st.title("🎥 NCC Video Training Guides")
    st.markdown("Browse through our collection of NCC training videos by category.")
    
    # Sidebar with category selection
    st.sidebar.header("Categories")
    selected_category = st.sidebar.radio(
        "Select a category:",
        options=list(NCC_VIDEOS.keys()),
        index=0
    )
    
    # Display selected category videos
    st.header(f"{selected_category} Training Videos")
    
    if selected_category in NCC_VIDEOS:
        videos = NCC_VIDEOS[selected_category]
        
        for video in videos:
            with st.expander(f"{video.title} ({video.duration})", expanded=True):
                # Video embed
                st.video(video.url)
                
                # Video details
                if video.description:
                    st.markdown(f"**Description:** {video.description}")
                
                # Add some space between videos
                st.markdown("---")
    else:
        st.warning("No videos available for this category.")
    
    # Add a feedback section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Feedback")
    feedback = st.sidebar.text_area("Suggest a video or category:")
    if st.sidebar.button("Submit Feedback"):
        if feedback:
            # In a real app, you would save this feedback to a database
            st.sidebar.success("Thank you for your feedback!")
        else:
            st.sidebar.warning("Please enter your feedback before submitting.")

# For testing the module directly
if __name__ == "__main__":
    display_video_guides()
