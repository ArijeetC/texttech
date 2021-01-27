import json, random
import pymongo
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
import re 

# Connect to a local instance of MongoDB
mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
movie_db = mongodb_client["final_movie_db1"]
movie_coll = movie_db["movie_coll"]

# Sentiment classifier object
classifier = pipeline('sentiment-analysis')

# # Return the sentiment of a given input sentence
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

# # Find the overall sentiment label and score for a given set of comments 
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

def stop_words_filter(word):
    return word not in stopwords.words('english')

def clean_text(text):
    clean_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+|\n|(\*)|(\(http(s)*.*\))|\[|\]", flags=re.UNICODE)
    text = clean_pattern.sub(r' ',text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+\.", ".", text)
    return text.strip()

# Insert the given list of movie data into the MongoDB collection created
def insert_into_db(movies_list):
    movie_coll.insert_many(movies_list)


if __name__ == "__main__":
    years = ["2015","2016","2017","2018","2019","2020"]
    for year in years:
        print(f"\nProcessing {year} data")
        filename = f"data/{year}_mov.json"

        movies_data = {}
        words_without_sw=[]

        with open(filename, "r") as f:
            movies_data = json.load(f)["movies_data"]

        for movie in movies_data:

            movie["comments"] = list(map(clean_text, movie["comments"]))
            movie["label"], movie["percentage"] = get_comment_sentiment(movie["comments"])
            words_list = " ".join(movie["comments"]).split(" ")
            
            #remove stopwords
            filtered_words = list(filter(stop_words_filter, words_list))

            #use pos-tagging to create adj_word_count
            pos_word=nltk.pos_tag(filtered_words)
            for pos in pos_word:
                if (pos[1] == 'JJ') or (pos[1] == 'JJR') or (pos[1] == 'JJS'):
                    words_without_sw.append(pos[0])

            movie["words"] = words_without_sw

        # with open(f"data/{year}_mov_sentiment_final3.json", "w", encoding="utf-8") as f:
        #     json.dump({"movies_data": movies_data}, f)
        insert_into_db(movies_data)
