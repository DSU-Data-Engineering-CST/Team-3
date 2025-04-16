import streamlit as st
import os
import json
import googleapiclient.discovery
import googleapiclient.errors
import re
from datetime import datetime, date, time
import sys
import pandas as pd

# --- Configuration & Constants ---
OUTPUT_DIR_APP = "youtube_app_output" # Optional: Define if needed elsewhere

# --- Helper Functions ---

# No changes needed for extract_video_id, but we won't use it as the primary input method
def extract_video_id(url_or_id):
    """Extracts YouTube video ID from URL or returns the ID if it's already an ID."""
    # ... (keep the function as before, might be useful for future features)
    if not url_or_id:
        return None
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url_or_id)
    if match:
        return match.group(1)
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id
    return None

@st.cache_data(ttl=3600) # Cache search results for an hour to save API quota
def search_youtube_videos(_youtube_client, query, max_results=10):
    """Searches YouTube for videos matching the query."""
    st.info(f"Searching YouTube for: '{query}'...")
    try:
        search_request = _youtube_client.search().list(
            part="snippet",
            q=query,
            type="video", # We only want videos
            maxResults=max_results
        )
        search_response = search_request.execute()
        videos = []
        for item in search_response.get("items", []):
            snippet = item.get("snippet", {})
            videos.append({
                "id": item.get("id", {}).get("videoId"),
                "title": snippet.get("title"),
                "channel": snippet.get("channelTitle"),
                "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url")
            })
        st.success(f"Found {len(videos)} potential video(s).")
        return videos, None # Return videos and no error
    except googleapiclient.errors.HttpError as e:
        err_msg = f"API Error during search: {e}"
        st.error(err_msg)
        return [], err_msg # Return empty list and error message
    except Exception as e:
        err_msg = f"Unexpected error during search: {e}"
        st.error(err_msg)
        return [], err_msg # Return empty list and error message

# Modify get_youtube_data slightly to accept the client object
# Add caching to avoid re-fetching if analyzing the same video again quickly
@st.cache_data(ttl=600) # Cache analysis results for 10 minutes
def get_youtube_data(_youtube_client, video_id, fetch_stats=True, fetch_comments=True):
    """Fetches selected YouTube data using a pre-built client."""
    data = {'title': None, 'views': 'N/A', 'likes': 'N/A', 'comments': [], 'error': None}
    if not _youtube_client:
         data['error'] = "YouTube client not initialized."
         return False, data

    try:
        # --- Get Video Details ---
        parts_to_request = ["snippet"]
        if fetch_stats: parts_to_request.append("statistics")

        st.info(f"Fetching video details (Parts: {', '.join(parts_to_request)})...")
        video_request = _youtube_client.videos().list(part=",".join(parts_to_request), id=video_id)
        video_response = video_request.execute()

        if not video_response.get("items"):
            data['error'] = f"Video with ID '{video_id}' not found or access restricted."
            st.error(data['error'])
            return False, data

        video_details = video_response["items"][0]
        data['title'] = video_details["snippet"]["title"]

        if fetch_stats and "statistics" in video_details:
            data['likes'] = video_details["statistics"].get("likeCount", "N/A")
            data['views'] = video_details["statistics"].get("viewCount", "N/A")
        elif fetch_stats:
             st.warning("Statistics requested but not found (might be disabled).")

        st.success(f"Fetched Details for: '{data['title']}'")
        if fetch_stats: st.write(f"Raw Stats - Views: {data['views']}, Likes: {data['likes']}")

        # --- Get Comments (if requested) ---
        if fetch_comments:
            st.info("Fetching comments...")
            comments_list = []
            next_page_token = None
            page_count = 0
            total_comments_processed = 0
            comment_fetch_error = None

            with st.spinner("Fetching comment pages..."):
                while True:
                    page_count += 1
                    try:
                        comments_request = _youtube_client.commentThreads().list(
                            part="snippet", videoId=video_id, maxResults=100,
                            pageToken=next_page_token, textFormat="plainText"
                        )
                        comments_response = comments_request.execute()
                        page_items = comments_response.get("items", [])

                        for item in page_items:
                            # ... (comment parsing logic remains the same) ...
                            comment_data = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                            comment_id = item.get("snippet", {}).get("topLevelComment", {}).get("id")
                            comments_list.append({
                                "comment_id": comment_id,
                                "author": comment_data.get("authorDisplayName", "N/A"),
                                "published_at": comment_data.get("publishedAt"),
                                "updated_at": comment_data.get("updatedAt"),
                                "comment_text": comment_data.get("textDisplay", ""),
                                "like_count": comment_data.get("likeCount", 0)
                            })

                        total_comments_processed += len(page_items)
                        next_page_token = comments_response.get("nextPageToken")
                        if not next_page_token:
                            st.info(f"Fetched all {total_comments_processed} comments.")
                            break
                    except googleapiclient.errors.HttpError as e:
                         # ... (error handling for comments remains the same) ...
                        error_details = json.loads(e.content.decode('utf-8')).get('error', {})
                        reason = error_details.get('errors', [{}])[0].get('reason')
                        if reason == 'commentsDisabled': comment_fetch_error = "Comments are disabled for this video."
                        else: comment_fetch_error = f"API error fetching comments (page {page_count}): {e}"
                        st.warning(comment_fetch_error)
                        next_page_token = None
                        break
                    except Exception as e:
                         comment_fetch_error = f"Unexpected error fetching comments: {e}"
                         st.warning(comment_fetch_error)
                         next_page_token = None
                         break

            data['comments'] = comments_list
            if comment_fetch_error and not data['error']: data['error'] = comment_fetch_error
        else:
            st.info("Comment fetching was not selected.")

        return True, data # Success

    except googleapiclient.errors.HttpError as e:
         # ... (critical error handling remains the same) ...
        error_content = e.content.decode('utf-8')
        try:
            error_details = json.loads(error_content).get('error', {})
            reason = error_details.get('errors', [{}])[0].get('reason', 'Unknown')
            message = error_details.get('message', str(e))
            data['error'] = f"API Error ({e.resp.status}): {reason} - {message}"
        except Exception: data['error'] = f"API Error: {e}. Details: {error_content}"
        st.error(data['error'])
        return False, data
    except Exception as e:
        data['error'] = f"CRITICAL Unexpected Error: {e}"
        st.error(data['error'])
        return False, data

# Keep filter_comments_by_date as it was
def filter_comments_by_date(comments, start_date, end_date):
    # ... (function remains the same) ...
    if not start_date and not end_date: return comments
    filtered_comments = []
    start_datetime = datetime.combine(start_date, time.min) if start_date else None
    end_datetime = datetime.combine(end_date, time.max) if end_date else None
    for comment in comments:
        try:
            published_dt = datetime.fromisoformat(comment['published_at'].replace('Z', '+00:00'))
            published_dt_naive = published_dt.replace(tzinfo=None)
            if start_datetime and published_dt_naive < start_datetime: continue
            if end_datetime and published_dt_naive > end_datetime: continue
            filtered_comments.append(comment)
        except Exception as e:
            st.warning(f"Date parse error for comment {comment.get('comment_id', '')}: {e}")
    return filtered_comments

# --- Streamlit App UI ---

st.set_page_config(layout="wide")
st.title("📊 YouTube Video Search & Analyzer")

# --- Session State Initialization ---
# Use session state to store results across reruns
if 'api_key' not in st.session_state: st.session_state.api_key = None
if 'youtube_client' not in st.session_state: st.session_state.youtube_client = None
if 'search_results' not in st.session_state: st.session_state.search_results = []
if 'search_error' not in st.session_state: st.session_state.search_error = None
if 'selected_video_id' not in st.session_state: st.session_state.selected_video_id = None
if 'selected_video_title' not in st.session_state: st.session_state.selected_video_title = None
if 'analysis_results' not in st.session_state: st.session_state.analysis_results = None
if 'analysis_error' not in st.session_state: st.session_state.analysis_error = None


# --- Sidebar Inputs ---
st.sidebar.header("API Configuration")
api_key_input = st.sidebar.text_input(
    "🔑 YouTube Data API v3 Key",
    type="password",
    help="Your Google Cloud API Key. Required for search and analysis.",
    value=st.session_state.api_key or "" # Persist key within session
)

# Store API Key and initialize client if key is provided and valid
if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input
    try:
        st.session_state.youtube_client = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=st.session_state.api_key
        )
        st.sidebar.success("API Client Initialized.")
        # Clear previous results if key changes
        st.session_state.search_results = []
        st.session_state.selected_video_id = None
        st.session_state.analysis_results = None
    except Exception as e:
        st.sidebar.error(f"Failed to initialize API client: {e}")
        st.session_state.youtube_client = None
        st.session_state.api_key = None # Reset invalid key

st.sidebar.header("1. Search Video")
search_query = st.sidebar.text_input("🔍 Enter search terms (e.g., 'movie trailer 2024')")
search_button = st.sidebar.button("Search Videos")

# --- Main Area Layout ---
col_main, col_results = st.columns([2, 1]) # Main analysis area, Search results sidebar-like area

with col_main:
    st.header("Video Analysis")
    if not st.session_state.api_key or not st.session_state.youtube_client:
         st.warning("Please enter a valid API Key in the sidebar to enable search and analysis.")

    # Display selected video and analysis options only when a video is selected
    if st.session_state.selected_video_id:
        st.subheader(f"Selected: {st.session_state.selected_video_title}")
        st.video(f"https://www.youtube.com/watch?v={st.session_state.selected_video_id}")

        st.markdown("---")
        st.subheader("2. Analysis Options")
        fetch_views_opt = st.checkbox("👁️ Fetch Views", value=True)
        fetch_likes_opt = st.checkbox("👍 Fetch Likes", value=True)
        fetch_comments_opt = st.checkbox("💬 Fetch Comments", value=True)
        fetch_stats_opt = fetch_views_opt or fetch_likes_opt # Helper flag

        st.subheader("Comment Filtering (Optional)")
        comment_start_date = st.date_input("📅 Start Date", value=None)
        comment_end_date = st.date_input("📅 End Date", value=date.today())

        analyze_button = st.button(f"📈 Analyze '{st.session_state.selected_video_title}'", type="primary")

        # --- Analysis Logic ---
        if analyze_button:
            st.session_state.analysis_results = None # Reset previous analysis
            st.session_state.analysis_error = None
            st.info(f"Starting analysis for Video ID: {st.session_state.selected_video_id}")
            success, result_data = get_youtube_data(
                st.session_state.youtube_client,
                st.session_state.selected_video_id,
                fetch_stats=fetch_stats_opt,
                fetch_comments=fetch_comments_opt
            )
            if success:
                st.session_state.analysis_results = result_data
                # Check for non-critical errors like disabled comments
                if result_data.get('error'):
                    st.session_state.analysis_error = result_data['error']
                    st.warning(f"Analysis completed with warnings: {st.session_state.analysis_error}")
                else:
                     st.success("Analysis complete.")
            else:
                st.session_state.analysis_error = result_data.get('error', "Unknown analysis error.")
                st.error(f"Analysis failed: {st.session_state.analysis_error}")

        # --- Display Analysis Results ---
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            st.markdown("---")
            st.header("Analysis Results")

            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("👁️ Views", results.get('views', 'N/A') if fetch_views_opt else "Not Fetched")
            res_col2.metric("👍 Likes", results.get('likes', 'N/A') if fetch_likes_opt else "Not Fetched")

            # Prepare data for download
            stats_data_str = f"Video Title: {results.get('title', 'N/A')}\nVideo ID: {st.session_state.selected_video_id}\n"
            if fetch_views_opt: stats_data_str += f"Views: {results.get('views', 'N/A')}\n"
            if fetch_likes_opt: stats_data_str += f"Likes: {results.get('likes', 'N/A')}\n"

            # Filter comments
            comments_to_display = results.get('comments', [])
            filtered_comments = comments_to_display # Start with all fetched
            if fetch_comments_opt and (comment_start_date or comment_end_date):
                filtered_comments = filter_comments_by_date(comments_to_display, comment_start_date, comment_end_date)
                st.write(f"Showing {len(filtered_comments)} comments out of {len(comments_to_display)} fetched (after date filtering).")
            elif not fetch_comments_opt:
                 filtered_comments = []

            res_col3.metric("💬 Comments Fetched", len(comments_to_display))

            # --- Download Buttons ---
            st.subheader("Downloads")
            dl_col1, dl_col2 = st.columns(2)
            dl_col1.download_button(
                label="💾 Download Stats (.txt)", data=stats_data_str,
                file_name=f"{st.session_state.selected_video_id}_stats.txt", mime="text/plain",
                disabled=not(fetch_views_opt or fetch_likes_opt)
            )
            dl_col2.download_button(
                label="💾 Download Comments (.json)", data=json.dumps(filtered_comments, indent=4, ensure_ascii=False),
                file_name=f"{st.session_state.selected_video_id}_comments_filtered.json", mime="application/json",
                disabled=not fetch_comments_opt
            )

            # --- Comments Preview ---
            if fetch_comments_opt and filtered_comments:
                st.subheader("Comments Preview (Filtered)")
                try:
                    df_comments = pd.DataFrame(filtered_comments)
                    st.dataframe(df_comments[['published_at', 'author', 'like_count', 'comment_text']])
                except Exception as e:
                    st.error(f"Error displaying comments table: {e}")
            elif fetch_comments_opt:
                 st.info("No comments to display.")

    else:
        st.info("⬅️ Please search for a video and select one from the results on the right to begin analysis.")


with col_results:
    st.header("Search Results")
    # --- Search Logic ---
    if search_button:
        st.session_state.search_results = [] # Clear previous search
        st.session_state.search_error = None
        st.session_state.selected_video_id = None # Clear selection on new search
        st.session_state.analysis_results = None # Clear analysis on new search

        if not st.session_state.youtube_client:
            st.error("API Client not initialized. Please enter a valid API Key.")
        elif not search_query:
            st.warning("Please enter a search query.")
        else:
            # Call the search function
            videos, error = search_youtube_videos(st.session_state.youtube_client, search_query)
            st.session_state.search_results = videos
            st.session_state.search_error = error # Store potential search error

    # --- Display Search Results ---
    if st.session_state.search_error:
         st.error(f"Search failed: {st.session_state.search_error}")

    if st.session_state.search_results:
        st.write(f"Found {len(st.session_state.search_results)} result(s):")
        for video in st.session_state.search_results:
            if video.get("id"): # Ensure there's a video ID
                 res_col_thumb, res_col_info = st.columns([1, 3])
                 with res_col_thumb:
                      if video.get("thumbnail"):
                           st.image(video["thumbnail"], width=120)
                 with res_col_info:
                      st.write(f"**{video.get('title', 'No Title')}**")
                      st.caption(f"Channel: {video.get('channel', 'N/A')}")
                      st.caption(f"ID: {video['id']}")
                      # Button to select this video for analysis
                      if st.button("Select for Analysis", key=f"select_{video['id']}"):
                           st.session_state.selected_video_id = video['id']
                           st.session_state.selected_video_title = video.get('title', 'Selected Video')
                           st.session_state.analysis_results = None # Clear old analysis
                           st.session_state.analysis_error = None
                           st.rerun() # Rerun to update the main panel immediately
                 st.markdown("---") # Separator between results
    elif search_button and not st.session_state.search_error: # Handle case where search was run but found nothing
         st.info("No videos found matching your query.")

# --- Footer/Sidebar Info ---
st.sidebar.markdown("---")
st.sidebar.caption("Note: API Key is stored only for this session.")
st.sidebar.caption("Likes/Views are totals and cannot be filtered by date.")
