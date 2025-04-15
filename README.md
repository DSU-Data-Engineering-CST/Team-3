
## Prerequisites ⚙️

1.  **Python:** Version 3.7 or higher installed.
2.  **pip:** Python package installer (usually comes with Python).
3.  **Google Cloud Account:** Required to access Google Cloud services.
4.  **Enabled YouTube Data API v3:** You need to create a project in Google Cloud Console, enable the "YouTube Data API v3", and generate credentials.
5.  **API Key:** Generate an API Key credential within your Google Cloud project for the YouTube Data API v3.
    *   **Important:** Keep your API Key secure! Do not commit it to version control.
    *   **API Quotas:** Be aware of the YouTube Data API's daily quota limits. Fetching data, especially comments for popular videos, consumes quota points. Check your usage in the Google Cloud Console.

## Installation & Setup 🚀

1.  **Clone the Repository (or Download Files):**
    ```bash
    # If using Git
    git clone <your-repository-url>
    cd youtube_etl_project
    ```
    Or download the necessary files (`youtube_app.py`, `.gitignore`, `.env.example`, `README.md`) into a project directory.

2.  **Create and Activate a Virtual Environment:**
    (Highly recommended to keep dependencies isolated)
    ```bash
    # Navigate to your project directory in the terminal
    cd path/to/youtube_etl_project

    # Create a virtual environment named 'venv'
    python -m venv venv

    # Activate the virtual environment:
    # Windows (cmd):
    venv\Scripts\activate.bat
    # Windows (PowerShell):
    # (You might need to run: Set-ExecutionPolicy Unrestricted -Scope Process)
    venv\Scripts\Activate.ps1
    # macOS / Linux:
    source venv/bin/activate
    ```
    Your terminal prompt should now indicate the active environment (e.g., `(venv) C:\...`).

3.  **Create `requirements.txt` (if it doesn't exist):**
    Make sure you have the following lines in a file named `requirements.txt`:
    ```txt
    streamlit
    google-api-python-client
    pandas
    openpyxl
    ```

4.  **Install Dependencies:**
    ```bash
    # Make sure your virtual environment is active!
    pip install -r requirements.txt
    ```

## Configuration 🔑

This Streamlit application primarily takes the **API Key** as direct input in the web interface sidebar for security reasons (it's not stored persistently).

While the `.env.example` file exists from potential earlier versions, it's not strictly necessary for running the `youtube_app.py` script, as the key is entered manually in the UI.

**Security Reminder:**
*   **NEVER** hardcode your API key directly into the `youtube_app.py` script.
*   **NEVER** commit your actual API key to Git or share it publicly.
*   Add `.env` (if you create one for other purposes) to your `.gitignore` file.

## Usage ▶️

1.  **Ensure Virtual Environment is Active:** If you open a new terminal, reactivate the venv (`source venv/bin/activate` or `venv\Scripts\activate`).
2.  **Run the Streamlit App:**
    ```bash
    streamlit run youtube_app.py
    ```
3.  **Open in Browser:** Streamlit will provide a local URL (usually `http://localhost:8501`). Open this URL in your web browser.
4.  **Interact with the UI:**
    *   Enter your **YouTube Data API v3 Key** in the sidebar field.
    *   Enter the **YouTube Video URL or just the Video ID** in the corresponding field.
    *   **Select** which data points (Views, Likes, Comments) you want to fetch using the checkboxes.
    *   Optionally, set **Start Date** and **End Date** filters for comments.
    *   Click the **"🚀 Fetch Data"** button.
5.  **View Results:** The app will show status messages, display fetched metrics (Views, Likes, Comments Count), and a preview table of the comments (if fetched and filtered).
6.  **Download Data:** Use the "Download Stats (.txt)" and "Download Comments (.json)" buttons to save the results locally. The comment file will contain the data *after* date filtering has been applied.

## Output Files 📄

When you use the download buttons in the Streamlit app:

*   **`[VideoID]_stats.txt`**: A simple text file containing:
    *   Video Title
    *   Video ID
    *   Views (if fetched)
    *   Likes (if fetched)
*   **`[VideoID]_comments_filtered.json`**: A JSON file containing an array of comment objects. Each object includes details like `comment_id`, `author`, `published_at`, `comment_text`, `like_count`, etc. This file reflects any date filtering applied in the UI.

## Troubleshooting 🛠️

*   **`streamlit: The term 'streamlit' is not recognized...`**:
    *   **Cause:** Streamlit is not installed OR your virtual environment is not active.
    *   **Fix:** Activate your venv (`source venv/bin/activate` or `venv\Scripts\activate`) and ensure you've run `pip install -r requirements.txt` within the active environment.
*   **`CRITICAL Unexpected Error: [WinError 10060] A connection attempt failed...`**:
    *   **Cause:** Network timeout connecting to Google's API servers. Often due to firewall blocking, proxy server issues, unstable internet, or (rarely) Google server problems.
    *   **Fix:** Check internet connection, temporarily disable firewall (for testing ONLY, then configure rules), configure proxy settings if needed (via `HTTP_PROXY`/`HTTPS_PROXY` environment variables), check DNS.
*   **`API Error (403): Forbidden` / `quotaExceeded`**:
    *   **Cause:** You've exceeded your daily YouTube Data API quota, or the API key doesn't have permission (ensure API is enabled in Google Cloud Console).
    *   **Fix:** Wait until the quota resets (usually midnight Pacific Time), request a quota increase (if needed), or check API key/project settings.
*   **`API Error (400): Bad Request` / `invalidKey`**:
    *   **Cause:** The API Key you entered is incorrect or invalid.
    *   **Fix:** Double-check the API Key value you entered. Ensure it was copied correctly from the Google Cloud Console.
*   **`Error: Video with ID 'https://...' not found`**:
    *   **Cause:** You pasted the full URL into the Video ID field when only the ID (the part after `v=`) was expected (though the current app version tries to handle this).
    *   **Fix:** Ensure you are providing either the correct full URL or just the 11-character Video ID (e.g., `dQw4w9WgXcQ`).
*   **Date Filtering Issues**: Ensure comment dates are parsed correctly. The YouTube API uses ISO 8601 format. If filtering seems off, check the date parsing logic in the `filter_comments_by_date` function.

## Contributing 🤝

Contributions are welcome! If you have suggestions for improvements or find bugs, please feel free to open an issue or submit a pull request (if this were on a platform like GitHub).

## License 📜

This project is licensed under the MIT License. *(You should create a separate file named `LICENSE` and add the full MIT license text to it).*

```text
MIT License

Copyright (c) [Year] [Your Name or Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
