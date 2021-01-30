import pymongo
import xmltodict

# Connect to a local instance of MongoDB
mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
movie_db = mongodb_client["movie_db"]
movie_coll = movie_db["movie_coll"]

# Define a pipeline for finding word count in Positive movie comments
pos_pipeline = [
    {
      "$match": {
         "label": "Positive"
      }
    },
    {
        "$unwind": "$words"
    },
    {
        "$group": {
            "_id": "$words",
            "count": {
                "$sum": 1
            }
        }
    },
    {
        "$project": {
            "_id": 0, "name": "$_id", "count": 1
        }
    }
]
results = list(movie_coll.aggregate(pos_pipeline))

# Generate an XML file from the results of aggregation pipeline query
wordcount_xml = xmltodict.unparse({"words": {"word": results}}, pretty=True)
with open("static/wordcount_pos.xml", "w", encoding="utf-8") as f:
    f.write(wordcount_xml)

# Define a pipeline for finding word count in Negative movie comments
neg_pipeline = [
    {
      "$match": {
         "label": "Negative"
      }
    },
    {
        "$unwind": "$words"
    },
    {
        "$group": {
            "_id": "$words",
            "count": {
                "$sum": 1
            }
        }
    },
    {
        "$project": {
            "_id": 0, "name": "$_id", "count": 1
        }
    }
]
results = list(movie_coll.aggregate(neg_pipeline))

# Generate an XML file from the results of aggregation pipeline query
wordcount_xml = xmltodict.unparse({"words": {"word": results}}, pretty=True)
with open("static/wordcount_neg.xml", "w", encoding="utf-8") as f:
    f.write(wordcount_xml)


# Query the database and find the list of positive and negative reviewed movies
pos_movs = movie_coll.find({"label": "Positive"}, {"_id":0, "comments":0, "words":0})
neg_movs = movie_coll.find({"label": "Negative"}, {"_id":0, "comments":0, "words":0})

pos_movs = list(pos_movs)
neg_movs = list(neg_movs)

# Generate XML files from the results of the database queries
pos_xml = xmltodict.unparse({"movies": {"movie": pos_movs}}, pretty=True)

with open("static/pos_movs.xml", "w", encoding="utf-8") as f:
    f.write(pos_xml)

neg_xml = xmltodict.unparse({"movies": {"movie": neg_movs}}, pretty=True)

with open("static/neg_movs.xml", "w", encoding="utf-8") as f:
    f.write(neg_xml)