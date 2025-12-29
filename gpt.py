import streamlit as st
import requests
from datetime import datetime, timedelta

# App Title
st.title("YouTube Viral History Topics Finder")

# API Key Input
API_KEY = st.text_input("Enter YouTube API Key:", type="password")

# YouTube API URLs
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# User Inputs
days = st.number_input(
    "Enter number of days to search (1–30):",
    min_value=1,
    max_value=30,
    value=7
)

# ✅ HISTORY KEYWORDS (Old ones removed)
keywords = [
    "medieval history",
    "military history",
    "history",
    "crusades",
    "knights",
    "ancient battles",
    "historical battles",
    "Europe history",
    "famous battles",
    "history channel",
    "historical events",
    "historical curiosities",
    "world history",
    "history facts",
    "legendary battles",
    "historical strategy",
    "history mysteries",
    "ancient civilizations",
    "history education",
    "epic battles",
    "forgotten history"
]

# Button
if st.button("Fetch Viral Videos"):

    if not API_KEY:
        st.error("❌ Please enter a valid YouTube API Key")
        st.stop()

    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        results = []

        for keyword in keywords:
            st.write(f"🔍 Searching: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY
            }

            search_response = requests.get(
                YOUTUBE_SEARCH_URL,
                params=search_params,
                timeout=10
            ).json()

            if "items" not in search_response:
                continue

            for item in search_response["items"]:
                video_id = item["id"].get("videoId")
                channel_id = item["snippet"].get("channelId")

                if not video_id or not channel_id:
                    continue

                # Video statistics
                video_stats = requests.get(
                    YOUTUBE_VIDEO_URL,
                    params={
                        "part": "statistics",
                        "id": video_id,
                        "key": API_KEY
                    },
                    timeout=10
                ).json()

                if not video_stats.get("items"):
                    continue

                views = int(
                    video_stats["items"][0]["statistics"].get("viewCount", 0)
                )

                # Channel statistics
                channel_stats = requests.get(
                    YOUTUBE_CHANNEL_URL,
                    params={
                        "part": "statistics",
                        "id": channel_id,
                        "key": API_KEY
                    },
                    timeout=10
                ).json()

                if not channel_stats.get("items"):
                    continue

                subs = int(
                    channel_stats["items"][0]["statistics"].get("subscriberCount", 0)
                )

                # Only small channels (viral potential)
                if subs < 3000:
                    results.append({
                        "title": item["snippet"].get("title", "N/A"),
                        "description": item["snippet"].get("description", "")[:200],
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "views": views,
                        "subs": subs
                    })

        # Display results
        if results:
            st.success(f"✅ Found {len(results)} potential viral history videos!")
            for r in results:
                st.markdown(
                    f"**Title:** {r['title']}  \n"
                    f"**Views:** {r['views']}  \n"
                    f"**Subscribers:** {r['subs']}  \n"
                    f"[▶ Watch Video]({r['url']})"
                )
                st.write("---")
        else:
            st.warning("No viral videos found under 3K subscribers.")

    except Exception as e:
        st.error(f"❌ Error occurred: {e}")
