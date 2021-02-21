import json, configparser, re, datetime, time
import requests
import praw
from praw.models import MoreComments
from bs4 import BeautifulSoup

# We'll be using two Reddit APIs here for fetching posts data
# The official Reddit API makes it difficult to find all posts in between two dates,
# so we are using an unofficial API known as Pushshift

# The Pushshift API will help us fetch the IDs of all posts,
# and using these IDs, we'll use the official Reddit API to fetch
# the comments of a post

# Read secrets for connecting to official Reddit 
config = configparser.ConfigParser()
config.read("config.ini")

username = config.get("SECRETS", "USERNAME")
password = config.get("SECRETS", "PASSWORD")
client_id = config.get("SECRETS", "CLIENT_ID")
client_secret = config.get("SECRETS", "CLIENT_SECRET")

# Set default headers that are needed while fetching webpages
headers = requests.utils.default_headers()
headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

# Create an instance of Reddit API object, this allows to access the API as a python object
reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret,
                    user_agent='Test-bot',
                    username=username,
                    password=password)

def get_reddit_posts(**kwargs):
    """Fetches all posts data from the Pushshift API
    
    Args:
        kwargs (dict): A dictionary of all parameters supported by the Pushshift API, such as subreddit, title, etc.

    Returns:
        A dictionary containing all data of a post from Pushshift API 
    """

    url = "https://api.pushshift.io/reddit/submission/search/"
    r = requests.get(url, params=kwargs, headers=headers)
    return r.json()["data"]

def get_reddit_post_ids(after, before, subreddit, title):
    """Gets the post IDs of all the movie discussion posts. Uses the Pushshift API to fetch post IDS

    Args:
        after (str): Get posts after this timestamp
        before (str): Get posts before this timestamp
        subreddit (str): Get posts only from this subreddit
        title (str): Get posts which contain this string in the title
    
    Returns:
        A list of strings, each string represents the ID of a Reddit post

    """
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

def get_comment_from_pushshift(id):
    """Gets comments from the Pushshift API since some comments get deleted and aren't available from the official Reddit API
    
    Args:
        id (str): ID of the comment that must be fetched
    
    Returns:
        A string which contains the content of the comment
    """

    url = "https://api.pushshift.io/reddit/search/comment/?ids="+str(id)
    r = requests.get(url, headers=headers)
    try:
        body = r.json()["data"][0]["body"]
    except Exception as exp:
        print(f"Error {str(exp)}")
        print(id)
        body = "NULL"
    return body

def get_comment_body(comment):
    """Retrieves the body from the Reddit API comment object.
    In case of deleted comments, retrieves it from Pushshift API
    
    Args:
        comment (object): Reddit API comment object

    Returns:
        A string which contains the content of the comment
    """

    body = comment.body
    if body == "[deleted]" or body == "[removed]":
        time.sleep(1)
        body = get_comment_from_pushshift(comment.id)
    return body

def get_movie_details(submission):
    """Gets information of a movie such as genre, director's name, etc.
    Uses BeautifulSoup to parse information in the webpage
    
    Args:
        submission (object): Reddit API submission (or post) object
    
    Returns:
        Strings containing the required information
    """

    text = submission.selftext
    genre, director = "NULL", "NULL"
    try:
        url_regex = re.compile("(?<=\()http(s)*:\/\/www.metacritic.com.*(?=\))")
        url = url_regex.search(text).group(0)

        time.sleep(1)
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.content, 'html.parser')

        for divtag in soup.find_all("div", {"class": "details_section"}):
            for div in divtag.find_all("div"):
                text = div.text.replace("\n", "")
                text = re.sub(r"\s+", " ", text)
                if "genre" in text.lower():
                    genre = text.split(":")[1]
                if "director" in text.lower():
                    director = text.split(":")[1]
    except Exception as exp:
        print(f"Error {str(exp)}")
        pass
    return genre, director

def get_post_comments(submission):
    """Gets the top 150 (or higest no. of comments) for a given Reddit post

    Args:
        submission (object): Reddit API submission (or post) object

    Returns:
        A list of strings, each represents a comment of the submission
    """
    
    comments = []
    submission.comment_sort = "top"
    submission.comment_limit = 100
    submission.comments.replace_more(limit=5)
    
    # Iterate over each comment in a submission
    for comment in submission.comments:
        # Fetch more available comments from Reddit API 
        if isinstance(comment, MoreComments):
            continue
        # Check if comment has minimum score
        if comment.score > 5:
            # Get content of the comment
            comment_body = get_comment_body(comment)
            if comment_body != "NULL": 
                comments.append(comment_body)
    comments = comments[:150]
    return comments


def get_posts(year):
    """Gets all the posts for given year and writes them to a JSON file
    Args:
        year (str): string representing the year for which data must be fetched
    
    """

    print(f"\n Fetching data for {year}")
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
            title = re.sub(r"^Official Discussion\s*(:|-)\s*|\s(\(20..\)\s)*\[.*\]?$", "", title).strip()
            temp["title"] = title
            temp["comments"] = get_post_comments(submission)
            temp["num_comments"] = num_comments
            temp["year"] = year
            genre, director = get_movie_details(submission)
            temp["genre"] = genre
            temp["director"] = director
            print(f"{title} - {genre} - {director}")
            movies_data.append(temp)

    print("\n Final movie posts = " + str(len(movies_data)))

    # Write the fetched data in a JSON file
    with open(f"data/{year}_mov.json", "w") as f:
        json.dump({"movies_data": movies_data}, f)


if __name__ == "__main__":
    """Runs a loop and fetches data for each year
    """

    years = ["2015", "2016", "2017", "2018", "2019", "2020"]

    for year in years:
        get_posts(year)