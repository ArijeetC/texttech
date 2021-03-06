import json, random
import pymongo
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
import re 

# Connect to a local instance of MongoDB
mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
movie_db = mongodb_client["movie_db"]
movie_coll = movie_db["movie_coll"]

# Sentiment classifier object
classifier = pipeline('sentiment-analysis')

def get_sentiment(sentence):
    """Returns the sentiment of a given input sentence
    
    Args:
        sentence (str): a string representing a user comment from Reddit 
    Returns:
        A string containing the label of the sentence ("positive"/"negative"/"neutral")
    """

    sentence = sentence[:1700]
    try:
        label = classifier(sentence)[0]["label"].lower()
    except Exception as exp:
        print(type(exp).__name__)
        print(len(sentence))
        print(sentence)
        label = "neutral"
    return label

def get_comment_sentiment(comments):
    """Finds the overall sentiment label and score for a given set of comments
    
    Args:
        comments (list): list of strings, each string represents a user comment
    
    Returns:
        A string representing the majority sentiment
        A float representing the percentage of comments with the majority sentiment 
    """

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
    """Checks if the given word is a stop word in English or not
    
    Args:
        word (str): string representing a word

    Returns:
        True if input word is not a stopword, otherwise False
    """

    return word not in stopwords.words('english')

def pos_tag_filter(word):
    """Determines the POS tag of the given word
    
    Args:
        word (str): string representing a word
    
    Returns:
        True if it is an adjective, otherwise False
    """

    adj_pos = False
    try:
        pos_tag = nltk.pos_tag([word])[0][1]
        if (pos_tag == 'JJ') or (pos_tag == 'JJR') or (pos_tag == 'JJS'):
            adj_pos = True
    except Exception:
        pass
    return adj_pos

def clean_text(text):
    """Cleans the given string by removing emojis, symbols, non-english characters, extra whitespaces
    
    Args:
        text (str): string representing a user comment from Reddit
    
    Returns:
        A string without any emojis, symbols, etc.
    """

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

def insert_into_db(movies_list):
    """Inserts the given list of movie data into the MongoDB collection created
    
    Args:
        movies_list (list): list of dictionaries, each dict contains data of a movie

    """
    movie_coll.insert_many(movies_list)


if __name__ == "__main__":
    """Runs a loop and processes data for each year
    """
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
            
            # #use pos-tagging to create adj_word_count
            adj_words = list(filter(pos_tag_filter, filtered_words))

            movie["words"] = adj_words

        insert_into_db(movies_data)
