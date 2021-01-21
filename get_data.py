import json, configparser, re, datetime, time
import requests
import praw
from praw.models import MoreComments

config = configparser.ConfigParser()
config.read("config.ini")

# We'll be using two Reddit APIs here for fetching posts data
# The official Reddit API makes it difficult to find all posts in between two dates,
# so we are using an unofficial API known as Pushshift

# The Pushshift API will help us fetch the IDs of all posts,
# and using these IDs, we'll use the official Reddit API to fetch
# the comments of a post

# Read secrets for connecting to official Reddit API
username = config.get("SECRETS", "USERNAME")
password = config.get("SECRETS", "PASSWORD")
client_id = config.get("SECRETS", "CLIENT_ID")
client_secret = config.get("SECRETS", "CLIENT_SECRET")

reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret,
                    user_agent='Test-bot',
                    username=username,
                    password=password)

# Fetch all posts data from the Pushshift API
def get_reddit_posts(**kwargs):
    url = "https://api.pushshift.io/reddit/submission/search/"
    r = requests.get(url, params=kwargs)
    return r.json()["data"]

# Get the post IDs of all the movie discussion posts
def get_reddit_post_ids(after, before, subreddit, title):
    post_ids = []
    posts_data = []
    
    before = before

    while True:
        if after > before:
            break
        
        posts = get_reddit_posts(subreddit=subreddit,
                                 title=title,
                                 before=str(before).split(".")[0],
                                 size=500,
                                 sort="desc",
                                 sort_type="created_utc")

        if not posts:
            break 
        
        for post in posts:
            before = float(post["created_utc"])
            if after > before:
                break
            posts_data.append(post)
        time.sleep(1)

    for post_data in posts_data:
        id = post_data["id"]
        title = post_data["title"]
        if re.match(r"^Official Discussion", title):
            post_ids.append(id)
    return post_ids

# Get the top 150 (or higest no. of comments) for a given Reddit post
def get_post_comments(submission):
    comments = []
    submission.comment_sort = "top"
    submission.comment_limit = 100
    submission.comments.replace_more(limit=5)
    for comment in submission.comments:
        if isinstance(comment, MoreComments):
            continue
        if comment.score > 5:
            comments.append(comment.body)
    comments = comments[:150]
    print(len(comments))
    return comments

def get_posts(year):

    print(f"Fetching data for {year}")
    # Get posts between start_date and end_date
    after = datetime.datetime(int(year)-1,12,31,23,59).timestamp()
    before = datetime.datetime(int(year)+1,1,1,0,0).timestamp() 

    subreddit = "movies"
    title = "Official Discussion"

    # Call pushshift and get post IDs for "Official discussions"
    post_ids = get_reddit_post_ids(after=after, before=before, subreddit=subreddit, title=title)

    print("Total posts = " + str(len(post_ids)))

    # # For each post_id, get title, comments, total_comment_count from the Reddit API
    movies_data = []

    for post_id in post_ids:
        temp = {}
        submission = reddit.submission(post_id)
        title = submission.title
        num_comments = submission.num_comments
        if num_comments > 25 and "megathread" not in title.lower():
            print(title)
            title = re.sub(r"^Official Discussion\s*(:|-)\s*|\s(\(20..\)\s)*\[.*\]?$", "", title)
            print(title)
            temp["title"] = title
            temp["comments"] = get_post_comments(submission)
            temp["num_comments"] = num_comments
            temp["year"] = year
            movies_data.append(temp)

    print("Final movie posts = " + str(len(movies_data)))

    # Write the fetched data in a JSON file
    with open(f"{year}_mov.json", "w") as f:
        json.dump({"movies_data": movies_data}, f)


if __name__ == "__main__":

    years = ["2015", "2016", "2017", "2018", "2019"]

    for year in years:
        get_posts(year)