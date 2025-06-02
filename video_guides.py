import streamlit as st
import json
import os

# Define the path to the videos.json file
VIDEO_DATA_PATH = os.path.join("data", "videos.json")

def video_guides():
    st.title("🎥 NCC Video Guides")
    st.write("Explore a collection of helpful videos related to NCC topics.")

    videos_data = {}
    file_version = None # Initialize version

    try:
        # Construct the absolute path to the JSON file
        script_dir = os.path.dirname(__file__)
        full_path = os.path.join(script_dir, VIDEO_DATA_PATH)

        if not os.path.exists(full_path):
            st.error(f"Video guide data not found at '{VIDEO_DATA_PATH}'. Please ensure the file exists.")
            st.info("Example structure for data/videos.json: {'version': '1.0', 'Drill': [{'title': 'Basic Drill', 'url': 'https://www.youtube.com/watch?v=example1', 'description': 'Learn basic drill movements.'}]}")
            return # Exit if data file is missing

        with open(full_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # --- Versioning Check ---
        file_version = raw_data.get("version")
        expected_version = "1.0" # Define your expected version
        if file_version != expected_version:
            st.warning(f"Video data file version mismatch. Expected '{expected_version}', but found '{file_version}'. "
                       "Functionality might be limited or incorrect. Please update your data/videos.json.")
            # You could add logic here to adapt to older versions if needed
            # For now, we'll proceed with the data as is, but warn the user.

        # Extract actual video categories data (excluding 'version' key)
        videos_data = {k: v for k, v in raw_data.items() if k != "version"}

        if not videos_data:
            st.warning("The video data file is empty or only contains version information. Please add video entries to data/videos.json.")
            return # Exit if data file is empty but exists

    except json.JSONDecodeError:
        st.error("Unable to parse video guide data. Please check if data/videos.json is a valid JSON file.")
        st.info("Ensure the JSON is correctly formatted, e.g., no trailing commas or syntax errors.")
        return # Exit if JSON is corrupt
    except Exception as e:
        st.error(f"An unexpected error occurred while loading video data: {e}")
        return

    # --- Category Selector ---
    categories = list(videos_data.keys())
    if not categories:
        st.info("No video categories found in the data file after loading.")
        return

    selected_category = st.selectbox(
        "Choose a Video Category:",
        categories,
        help="Select a category to view relevant videos."
    )

    st.markdown("---")

    # --- Search / Filter ---
    search_query = st.text_input(
        "Search Videos:",
        placeholder="e.g., 'parade', 'map reading', 'first aid'",
        help="Filter videos by title or description."
    ).lower() # Convert to lowercase for case-insensitive search

    st.markdown("---")

    # Display videos for the selected category
    if selected_category and selected_category in videos_data:
        category_videos = videos_data[selected_category]
        filtered_videos = []
        required_keys = {"title", "url"} # Define required keys for each video entry

        # Apply search filter and perform validation
        for video in category_videos:
            # --- JSON Schema Validation (Required Keys Check) ---
            if not required_keys.issubset(video.keys()):
                missing_keys = required_keys - video.keys()
                st.error(f"Video entry in category '{selected_category}' is missing required keys: {missing_keys}. Video: {video.get('title', 'Untitled')}. Skipping this entry.")
                continue # Skip this invalid video entry

            # Apply search filter
            title = video.get("title", "").lower()
            description = video.get("description", "").lower()
            if search_query in title or search_query in description:
                filtered_videos.append(video)
        
        if filtered_videos:
            st.subheader(f"Videos in '{selected_category}' Category:")
            for vid in filtered_videos:
                title = vid.get("title", "Untitled Video")
                url = vid.get("url")
                description = vid.get("description", "")

                # URL presence is already checked by required_keys, but good to be explicit for display
                if url:
                    st.markdown(f"**{title}**")
                    st.video(url) # Embed YouTube player
                    if description:
                        st.markdown(f"*{description}*")
                    st.markdown("---")
                else:
                    # This case should ideally be caught by required_keys check, but as a safeguard
                    st.warning(f"Video '{title}' in category '{selected_category}' has no URL provided and will not be displayed.")
        else:
            # Fallback message for no videos in category or no search results
            if search_query:
                st.info(f"No videos found matching '{search_query}' in the '{selected_category}' category.")
            else:
                st.info(f"No videos found for the '{selected_category}' category.")
    else:
        st.info("Please select a video category from the dropdown.")

    # --- Offline Mode Note ---
    st.markdown("---")
    st.markdown("""
    **Note on Offline Mode:**
    For true offline access, videos would need to be downloaded and stored locally (e.g., as MP4 files in an `assets/videos/` folder).
    The `st.video()` function can play local files if their paths are provided.
    Implementing this would require a mechanism to download videos and manage their local file paths,
    which is beyond the scope of this direct Streamlit application without a backend or pre-downloaded assets.
    """)

