import streamlit as st
import os
import json
import googleapiclient.discovery
import googleapiclient.errors
import re
from datetime import datetime, date, time # Import time explicitly
import sys
import pandas as pd # Useful for displaying data nicely

# --- Configuration & Constants ---
OUTPUT_DIR_APP = "youtube_app_output" # Separate output dir for app downloads if needed

# --- Helper Functions ---

def extract_video_id(url_or_id):
    """Extracts YouTube video ID from URL or returns the ID if it's already an ID."""
    if not url_or_id:
        return None
    # Regex to find YouTube video ID in various URL formats
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url_or_id)
    if match:
        return match.group(1)
    # Check if the input itself is potentially a valid ID (11 characters, specific characters)
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id
    return None

def get_youtube_data(api_key, video_id, fetch_stats=True, fetch_comments=True):
    """
    Fetches selected YouTube data. Modified to accept flags.
    Returns: (success_flag, data_dict)
    data_dict contains: 'title', 'views', 'likes', 'comments', 'error'
    """
    data = {'title': None, 'views': 'N/A', 'likes': 'N/A', 'comments': [], 'error': None}
    youtube = None
    try:
        st.info("Initializing YouTube API client...")
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        st.info("API client initialized.")

        # --- Get Video Details (Always get snippet for Title, optionally stats) ---
        parts_to_request = ["snippet"]
        if fetch_stats:
            parts_to_request.append("statistics")

        st.info(f"Fetching video details (Parts: {', '.join(parts_to_request)})...")
        video_request = youtube.videos().list(
            part=",".join(parts_to_request),
            id=video_id
        )
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
             st.warning("Statistics were requested but not found in the API response (might be disabled for the video).")

        st.success(f"Found Video: '{data['title']}'")
        if fetch_stats:
            st.write(f"Raw Stats - Views: {data['views']}, Likes: {data['likes']}")

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
                    # st.write(f"  Fetching comments page {page_count}...") # Can be too verbose
                    try:
                        comments_request = youtube.commentThreads().list(
                            part="snippet",
                            videoId=video_id,
                            maxResults=100,
                            pageToken=next_page_token,
                            textFormat="plainText"
                        )
                        comments_response = comments_request.execute()
                        page_items = comments_response.get("items", [])

                        for item in page_items:
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
                        # st.write(f"  Page {page_count}: Fetched {len(page_items)}. Total: {total_comments_processed}")

                        next_page_token = comments_response.get("nextPageToken")
                        if not next_page_token:
                            st.info(f"Fetched all {total_comments_processed} comments.")
                            break
                        # time.sleep(0.1) # Optional delay

                    except googleapiclient.errors.HttpError as e:
                        error_details = json.loads(e.content.decode('utf-8')).get('error', {})
                        reason = error_details.get('errors', [{}])[0].get('reason')
                        if reason == 'commentsDisabled':
                             comment_fetch_error = "Comments are disabled for this video."
                             st.warning(comment_fetch_error)
                        else:
                             comment_fetch_error = f"API error fetching comments (page {page_count}): {e}"
                             st.warning(comment_fetch_error)
                        next_page_token = None # Stop fetching
                        break
                    except Exception as e:
                        comment_fetch_error = f"Unexpected error fetching comments: {e}"
                        st.warning(comment_fetch_error)
                        next_page_token = None # Stop fetching
                        break

            data['comments'] = comments_list
            if comment_fetch_error:
                # Include comment fetch error in main error if it's the only one
                 if not data['error']: data['error'] = comment_fetch_error
        else:
            st.info("Comment fetching was not selected.")

        return True, data # Success

    except googleapiclient.errors.HttpError as e:
        error_content = e.content.decode('utf-8')
        try:
             error_details = json.loads(error_content).get('error', {})
             reason = error_details.get('errors', [{}])[0].get('reason', 'Unknown Reason')
             message = error_details.get('message', str(e))
             data['error'] = f"API Error ({e.resp.status}): {reason} - {message}"
        except Exception:
             data['error'] = f"API Error: {e}. Could not parse details: {error_content}"
        st.error(data['error'])
        return False, data # Failure
    except Exception as e:
        data['error'] = f"CRITICAL Unexpected Error: {e}"
        st.error(data['error'])
        return False, data # Failure

def filter_comments_by_date(comments, start_date, end_date):
    """Filters a list of comments based on 'published_at' date."""
    if not start_date and not end_date:
        return comments # No filtering needed

    filtered_comments = []
    # Combine date and time(min/max) for proper comparison range
    start_datetime = datetime.combine(start_date, time.min) if start_date else None
    end_datetime = datetime.combine(end_date, time.max) if end_date else None

    for comment in comments:
        try:
            # YouTube API provides ISO 8601 format (e.g., '2023-10-27T10:00:00Z')
            # Need to parse it correctly. Handle potential timezone 'Z' (UTC).
            published_dt = datetime.fromisoformat(comment['published_at'].replace('Z', '+00:00'))
            # Make it offset-naive for simple comparison IF start/end are naive (which st.date_input provides)
            published_dt_naive = published_dt.replace(tzinfo=None)

            if start_datetime and published_dt_naive < start_datetime:
                continue # Skip if before start date
            if end_datetime and published_dt_naive > end_datetime:
                continue # Skip if after end date
            filtered_comments.append(comment)
        except Exception as e:
            st.warning(f"Could not parse date for comment {comment.get('comment_id', '')}: {comment.get('published_at')} - Error: {e}")
            # Optionally include comments with parsing errors, or skip them
            # filtered_comments.append(comment) # Include if desired despite error

    return filtered_comments

# --- Streamlit App UI ---

st.set_page_config(layout="wide")
st.title("📊 YouTube Data Extractor")

# --- Inputs ---
st.sidebar.header("Inputs")
api_key_input = st.sidebar.text_input("🔑 YouTube Data API v3 Key", type="password", help="Your Google Cloud API Key")
video_url_or_id_input = st.sidebar.text_input("📺 YouTube Video URL or ID", help="e.g., https://www.youtube.com/watch?v=...")

st.sidebar.header("Data Selection")
fetch_views_opt = st.sidebar.checkbox("👁️ Fetch Views", value=True)
fetch_likes_opt = st.sidebar.checkbox("👍 Fetch Likes", value=True)
fetch_comments_opt = st.sidebar.checkbox("💬 Fetch Comments", value=True)

st.sidebar.header("Comment Filtering (Optional)")
comment_start_date = st.sidebar.date_input("📅 Start Date (for comments)", value=None) # No default start
comment_end_date = st.sidebar.date_input("📅 End Date (for comments)", value=date.today()) # Default to today

# Combine fetch_views_opt and fetch_likes_opt for the API call logic
fetch_stats_opt = fetch_views_opt or fetch_likes_opt

# --- Action Button ---
fetch_button = st.sidebar.button("🚀 Fetch Data", type="primary")

# --- Session State Initialization ---
# Use session state to store results across reruns after button click
if 'fetch_results' not in st.session_state:
    st.session_state.fetch_results = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'video_id' not in st.session_state:
    st.session_state.video_id = None

# --- Processing Logic ---
if fetch_button:
    # Reset state on new fetch attempt
    st.session_state.fetch_results = None
    st.session_state.error_message = None
    st.session_state.video_id = None

    st.info("Attempting to fetch data...")
    # Validate inputs
    if not api_key_input:
        st.error("API Key is required.")
        st.stop() # Stop execution if no API key

    extracted_id = extract_video_id(video_url_or_id_input)
    if not extracted_id:
        st.error("Invalid YouTube URL or Video ID provided.")
        st.stop() # Stop execution

    st.session_state.video_id = extracted_id # Store the extracted ID

    # Call the main data fetching function
    success, result_data = get_youtube_data(
        api_key_input,
        extracted_id,
        fetch_stats=fetch_stats_opt,
        fetch_comments=fetch_comments_opt
    )

    if success:
        st.session_state.fetch_results = result_data
        st.session_state.error_message = result_data.get('error') # Store non-critical errors too
        st.success("Data fetching process completed.")
        if st.session_state.error_message:
             st.warning(f"Completed with warnings: {st.session_state.error_message}")
    else:
        st.session_state.error_message = result_data.get('error', "An unknown critical error occurred.")
        st.error(f"Data fetching failed: {st.session_state.error_message}")
   

# --- Display Results ---
st.markdown("---") # Separator
st.header("Results")

if st.session_state.fetch_results:
    results = st.session_state.fetch_results
    video_title = results.get('title', 'N/A')
    st.subheader(f"Video: {video_title} (ID: {st.session_state.video_id})")

    col1, col2, col3 = st.columns(3)
    if fetch_views_opt:
        col1.metric("👁️ Views", results.get('views', 'N/A'))
    else:
        col1.metric("👁️ Views", "Not Fetched")

    if fetch_likes_opt:
        col2.metric("👍 Likes", results.get('likes', 'N/A'))
    else:
        col2.metric("👍 Likes", "Not Fetched")

    # Prepare data for download
    stats_data_str = f"Video Title: {video_title}\nVideo ID: {st.session_state.video_id}\n"
    if fetch_views_opt:
        stats_data_str += f"Views: {results.get('views', 'N/A')}\n"
    if fetch_likes_opt:
        stats_data_str += f"Likes: {results.get('likes', 'N/A')}\n"

    # Filter comments if applicable
    comments_to_display = results.get('comments', [])
    if fetch_comments_opt and (comment_start_date or comment_end_date):
        st.info(f"Filtering comments between {comment_start_date or 'Beginning'} and {comment_end_date or 'End'}...")
        original_count = len(comments_to_display)
        comments_to_display = filter_comments_by_date(comments_to_display, comment_start_date, comment_end_date)
        st.write(f"Showing {len(comments_to_display)} comments out of {original_count} fetched after date filtering.")
    elif not fetch_comments_opt:
         st.write("Comments were not fetched.")
         comments_to_display = [] # Ensure it's an empty list

    col3.metric("💬 Comments Fetched", len(results.get('comments', []))) # Show total fetched before filtering

    st.markdown("---")

    # --- Download Buttons ---
    st.subheader("Downloads")
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
         st.download_button(
            label="💾 Download Stats (.txt)",
            data=stats_data_str,
            file_name=f"{st.session_state.video_id}_stats.txt",
            mime="text/plain",
            disabled=not(fetch_views_opt or fetch_likes_opt) # Disable if neither was selected
        )

    with dl_col2:
        # Prepare comments for JSON download (use the potentially filtered list)
        comments_json_str = json.dumps(comments_to_display, indent=4, ensure_ascii=False)
        st.download_button(
            label="💾 Download Comments (.json)",
            data=comments_json_str,
            file_name=f"{st.session_state.video_id}_comments_filtered.json",
            mime="application/json",
            disabled=not fetch_comments_opt # Disable if comments weren't fetched
        )

    # --- Comments Preview ---
    if fetch_comments_opt and comments_to_display:
        st.subheader("Comments Preview (Filtered)")
        # Use pandas DataFrame for a nice table display
        try:
            df_comments = pd.DataFrame(comments_to_display)
            # Optionally select/reorder columns for display
            st.dataframe(df_comments[['published_at', 'author', 'like_count', 'comment_text']])
        except Exception as e:
            st.error(f"Error displaying comments table: {e}")
            st.write(comments_to_display[:10]) # Fallback to raw display
    elif fetch_comments_opt:
         st.info("No comments to display (either none found, none matched filter, or fetching failed).")


elif st.session_state.error_message:
    st.error(f"Could not display results due to previous error: {st.session_state.error_message}")
else:
    st.info("Enter API Key, Video URL/ID, select options, and click 'Fetch Data' to begin.")

st.sidebar.markdown("---")
st.sidebar.caption("Note: API Key is not stored. Use with caution.")
st.sidebar.caption("Likes/Views are totals and cannot be filtered by date via this method.")