# --- youtube_data_extractor.py ---
import os
import json
import googleapiclient.discovery
import googleapiclient.errors
import sys
import time # Optional: for potential rate limiting delays

# --- Configuration ---
# Load from environment variables for security and flexibility
API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")
OUTPUT_DIR = "youtube_output_data" # Name of the directory to save output files

# --- Pre-run Checks ---
if not API_KEY:
    print("Error: YOUTUBE_API_KEY environment variable not set.")
    print("Please set this variable before running the script.")
    print("Example (Linux/macOS): export YOUTUBE_API_KEY=\"YOUR_KEY\"")
    print("Example (Windows CMD): set YOUTUBE_API_KEY=\"YOUR_KEY\"")
    print("Example (Windows PowerShell): $env:YOUTUBE_API_KEY=\"YOUR_KEY\"")
    sys.exit(1) # Exit with a non-zero status code to indicate failure

if not VIDEO_ID:
    print("Error: YOUTUBE_VIDEO_ID environment variable not set.")
    print("Please set this variable before running the script.")
    print("Example (Linux/macOS): export YOUTUBE_VIDEO_ID=\"VIDEO_ID\"")
    print("Example (Windows CMD): set YOUTUBE_VIDEO_ID=\"VIDEO_ID\"")
    print("Example (Windows PowerShell): $env:YOUTUBE_VIDEO_ID=\"VIDEO_ID\"")
    sys.exit(1) # Exit with a non-zero status code to indicate failure

# Create output directory if it doesn't exist
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating output directory '{OUTPUT_DIR}': {e}")
    sys.exit(1)

# --- Functions ---

def get_youtube_data(api_key, video_id):
    """
    Fetches video details (title, likes, views) and all comments for a given YouTube video ID.

    Args:
        api_key (str): Your YouTube Data API v3 key.
        video_id (str): The ID of the YouTube video.

    Returns:
        tuple: (movie_name, likes, views, comments_list) on success,
               or (None, None, None, None) on critical API error.
               comments_list might be empty or incomplete if only comment fetching fails.
    """
    youtube = None # Initialize youtube object outside try block
    try:
        print(f"Initializing YouTube API client...")
        # Build the service object
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        print("API client initialized.")

        # --- Get Video Details (Title, Likes, Views) ---
        print(f"Fetching video details for Video ID: {video_id}...")
        video_request = youtube.videos().list(
            part="snippet,statistics", # Request snippet for title, statistics for counts
            id=video_id
        )
        video_response = video_request.execute()

        # Check if any video items were returned
        if not video_response.get("items"):
            print(f"Error: Video with ID '{video_id}' not found or access is restricted.")
            return None, None, None, None # Indicate critical failure

        video_details = video_response["items"][0]
        movie_name = video_details["snippet"]["title"]
        # Use .get() with default 0 for statistics that might be disabled by the uploader
        likes = video_details["statistics"].get("likeCount", "N/A") # Likes might be hidden
        views = video_details["statistics"].get("viewCount", "N/A") # Views are usually available

        print(f"Found Video: '{movie_name}', Views: {views}, Likes: {likes}")

        # --- Get Comments (with Pagination) ---
        print("Fetching comments (this may take a while for popular videos)...")
        comments_list = []
        next_page_token = None
        page_count = 0
        total_comments_processed = 0

        while True:
            page_count += 1
            print(f"  Fetching comments page {page_count}...")
            try:
                # Make the API request for a page of comment threads
                comments_request = youtube.commentThreads().list(
                    part="snippet", # Request snippet which contains comment details
                    videoId=video_id,
                    maxResults=100, # Max allowed per page by the API
                    pageToken=next_page_token, # Token for the next page, None for the first page
                    textFormat="plainText" # Get plain text comments, easier to process
                )
                comments_response = comments_request.execute()

                # Process each comment item on the current page
                page_items = comments_response.get("items", [])
                for item in page_items:
                    # Navigate the complex structure to get the top-level comment details
                    comment_data = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                    comment_id = item.get("snippet", {}).get("topLevelComment", {}).get("id")

                    # Extract desired fields, using .get() for safety
                    comments_list.append({
                        "comment_id": comment_id,
                        "author": comment_data.get("authorDisplayName", "Unknown Author"),
                        "published_at": comment_data.get("publishedAt"),
                        "updated_at": comment_data.get("updatedAt"),
                        "comment_text": comment_data.get("textDisplay", ""), # or textOriginal
                        "like_count": comment_data.get("likeCount", 0)
                    })

                total_comments_processed += len(page_items)
                print(f"  Fetched {len(page_items)} comments on this page. Total processed: {total_comments_processed}")

                # Check if there's a next page token
                next_page_token = comments_response.get("nextPageToken")
                if not next_page_token:
                    print("Fetched all available comment pages.")
                    break # Exit the loop if no more pages

                # Optional: Add a small delay to respect potential rate limits, especially for many pages
                # time.sleep(0.1)

            except googleapiclient.errors.HttpError as e:
                # Handle errors specifically during comment fetching (e.g., comments disabled)
                error_details = json.loads(e.content.decode('utf-8')).get('error', {})
                reason = error_details.get('errors', [{}])[0].get('reason')
                if reason == 'commentsDisabled':
                    print(f"Warning: Comments are disabled for video ID '{video_id}'. No comments fetched.")
                else:
                    print(f"Warning: API error fetching comments page {page_count}: {e}")
                    print("Stopping comment fetching for this video due to error.")
                # Don't treat this as a critical failure of the whole script, just break comment loop
                next_page_token = None # Ensure loop terminates
                break
            except Exception as e:
                print(f"Warning: An unexpected error occurred during comment fetching: {e}")
                print("Stopping comment fetching for this video due to error.")
                next_page_token = None # Ensure loop terminates
                break

        print(f"Finished fetching comments. Total unique comments collected: {len(comments_list)}")
        return movie_name, likes, views, comments_list

    except googleapiclient.errors.HttpError as e:
        # Handle critical API errors (e.g., invalid API key, quota exceeded)
        print(f"CRITICAL API Error occurred: {e}")
        error_content = e.content.decode('utf-8')
        print(f"Error details: {error_content}")
        # Attempt to parse error reason for better feedback
        try:
            error_details = json.loads(error_content).get('error', {})
            reason = error_details.get('errors', [{}])[0].get('reason')
            message = error_details.get('message', 'No specific message.')
            print(f"Reason: {reason} - Message: {message}")
            if e.resp.status == 403:
                 print("This might be a Quota Exceeded error or API Key restriction.")
            elif e.resp.status == 400:
                 print("This might be an Invalid API Key or malformed request.")
        except Exception:
            print("Could not parse detailed error reason from response.")
        return None, None, None, None # Indicate critical failure
    except Exception as e:
        # Handle other unexpected errors during setup or video detail fetching
        print(f"CRITICAL Unexpected Error occurred: {e}")
        return None, None, None, None # Indicate critical failure
    finally:
         # Optional: Close the client if needed, though usually not necessary for this library
         if youtube:
             try:
                 # There isn't a standard close/quit method for the discovery client object
                 # Resources are typically managed automatically or by the underlying http library
                 pass
             except Exception as e:
                 print(f"Note: Error during hypothetical client cleanup: {e}")


# --- Main Execution Block ---
if __name__ == "__main__":
    print("--- Starting YouTube Data Collection Script ---")

    # Call the function to get data
    movie_name, likes, views, comments = get_youtube_data(API_KEY, VIDEO_ID)

    # Proceed only if the critical data fetching (video details) was successful
    if movie_name is not None:
        print("\n--- Saving Data ---")

        # --- Save Video Statistics ---
        # Note: 'w' mode overwrites the file completely each time the script runs.
        stats_file_path = os.path.join(OUTPUT_DIR, "video_stats.txt")
        try:
            print(f"Saving video stats to: {stats_file_path}")
            with open(stats_file_path, "w", encoding='utf-8') as f:
                f.write(f"Video Title: {movie_name}\n")
                f.write(f"Video ID: {VIDEO_ID}\n")
                f.write(f"Views: {views}\n")
                f.write(f"Likes: {likes}\n") # Likes might be 'N/A'
            print("✅ Video stats saved successfully.")
        except IOError as e:
            print(f"Error: Failed to write stats file '{stats_file_path}': {e}")
            # Decide if this is critical enough to exit
            # sys.exit(1)

        # --- Save Comments ---
        # Save comments even if the list is empty (e.g., if comments were disabled)
        comments_file_path = os.path.join(OUTPUT_DIR, "comments.json")
        try:
            print(f"Saving {len(comments)} comments to: {comments_file_path}")
            with open(comments_file_path, "w", encoding='utf-8') as f:
                # Use ensure_ascii=False for proper handling of non-ASCII characters (e.g., emojis, other languages)
                json.dump(comments, f, indent=4, ensure_ascii=False)
            print("✅ Comments saved successfully.")
        except IOError as e:
            print(f"Error: Failed to write comments file '{comments_file_path}': {e}")
            # sys.exit(1)
        except TypeError as e:
             print(f"Error: Failed to serialize comments to JSON: {e}")
             # sys.exit(1)

        print("\n--- YouTube Data Collection Finished ---")
        sys.exit(0) # Explicitly exit with success code

    else:
        # This block executes if get_youtube_data returned None, indicating a critical error
        print("\n--- YouTube Data Collection Failed Due to Critical Error ---")
        print("Please check the error messages above, especially API Key, Video ID, and Quotas.")
        sys.exit(1) # Exit with failure code