import praw
import json
from datetime import datetime

# Rddit API seetup
reddit = praw.Reddit(
    client_id="wMrHJnzfgnWlsX1BD3hmMQ",  
    client_secret="MH2SiZyQ1_-cmD1Dn6NY7utR3PVYCQ",  
    user_agent="python:RemoteWorkSentiment:v1.0 (by /u/Signal-Physics8294)"
)

# Subreddits relevant to remote work
subreddits = ["WorkFromHome", "remotework", "wfh", "freelance", "WorkOnline", "overemployed", "RemoteJobs"]

# Define time windows
pre_covid_start = datetime(2018, 1, 1).timestamp()  # Pre-COVID: 2018-2019
pre_covid_end = datetime(2019, 12, 31).timestamp()
post_covid_start = datetime(2022, 1, 1).timestamp()  # Post-COVID: 2022 onward

pre_covid_data = []
post_covid_data = []

for subreddit_name in subreddits:
    try:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Scraping r/{subreddit_name}...")

        for post in subreddit.top(time_filter="all", limit=600):  
            post_time = post.created_utc
            
            # Categorize into pre-COVID or post-COVID
            if pre_covid_start <= post_time <= pre_covid_end:
                post_data = {
                    "subreddit": subreddit_name,
                    "title": post.title,
                    "text": post.selftext if post.selftext else "",
                    "upvotes": post.score,
                    "url": post.url,
                    "timestamp": datetime.fromtimestamp(post_time).strftime("%Y-%m-%d %H:%M:%S"),
                    "comments": []
                }
                post.comments.replace_more(limit=0)
                for comment in post.comments[:5]:
                    if comment.body and pre_covid_start <= comment.created_utc <= pre_covid_end:
                        post_data["comments"].append({
                            "text": comment.body,
                            "upvotes": comment.score,
                            "timestamp": datetime.fromtimestamp(comment.created_utc).strftime("%Y-%m-%d %H:%M:%S")
                        })
                pre_covid_data.append(post_data)

            elif post_time >= post_covid_start:
                post_data = {
                    "subreddit": subreddit_name,
                    "title": post.title,
                    "text": post.selftext if post.selftext else "",
                    "upvotes": post.score,
                    "url": post.url,
                    "timestamp": datetime.fromtimestamp(post_time).strftime("%Y-%m-%d %H:%M:%S"),
                    "comments": []
                }
                post.comments.replace_more(limit=0)
                for comment in post.comments[:5]:
                    if comment.body and comment.created_utc >= post_covid_start:
                        post_data["comments"].append({
                            "text": comment.body,
                            "upvotes": comment.score,
                            "timestamp": datetime.fromtimestamp(comment.created_utc).strftime("%Y-%m-%d %H:%M:%S")
                        })
                post_covid_data.append(post_data)

    except Exception as e:
        print(f"Error with r/{subreddit_name}: {e}")

# Save to separate JSON files
with open("reddit_pre_covid_remote_work.json", "w", encoding="utf-8") as f:
    json.dump(pre_covid_data, f, indent=4, ensure_ascii=False)
with open("reddit_post_covid_remote_work.json", "w", encoding="utf-8") as f:
    json.dump(post_covid_data, f, indent=4, ensure_ascii=False)

print(f"Scraped {len(pre_covid_data)} pre-COVID posts and {len(post_covid_data)} post-COVID posts.")
print("Saved to reddit_pre_covid_remote_work.json and reddit_post_covid_remote_work.json")