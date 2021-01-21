import json, random
import pymongo
from transformers import pipeline

# Connect to a local instance of MongoDB
mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
movie_db = mongodb_client["movie_db"]
movie_coll = movie_db["movie_coll"]

# Sentiment classifier object
classifier = pipeline('sentiment-analysis')

# Return the sentiment of a given input sentence
def get_sentiment(sentence):
    sentence = sentence[:1700]
    try:
        label = classifier(sentence)[0]["label"].lower()
    except Exception as exp:
        print(type(exp).__name__)
        print(len(sentence))
        print(sentence)
        label = "neutral"
    return label

# Find the overall sentiment label and score for a given set of comments 
def get_comment_sentiment(comments):
    total_count = len(comments)
    pos_count = 0
    neg_count = 0
    for comment in comments:
        comment_label = get_sentiment(comment)
        if comment_label == "positive":
            pos_count += 1
        else:
            neg_count += 1
    if pos_count >= neg_count:
        label = "Positive"
        score = pos_count/total_count * 100
    else:
        label = "Negative"
        score = neg_count/total_count * 100
    return label, score

# Insert the given list of movie data into the MongoDB collection created
def insert_into_db(movies_list):
    movie_coll.insert_many(movies_list)


if __name__ == "__main__":
    years = ["2015","2016","2017","2018","2019","2020"]
    for year in years:
        print(f"\nProcessing {year} data")
        filename = f"data/{year}_mov.json"

        movies_data = {}

        with open(filename, "r") as f:
            movies_data = json.load(f)["movies_data"]

        for movie in movies_data:
            movie["label"], movie["percentage"] = get_comment_sentiment(movie["comments"])

            # print(movie["comments"])
            movie["words"] = "".join(movie["comments"]).split(" ")
            # print(movie["words"])
            # break
        insert_into_db(movies_data)