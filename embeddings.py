import os
import re

import pandas as pd
import pinecone
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize pinecone client
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY", ""),
    environment=os.getenv("PINECONE_ENVIRONMENT", ""),
)
index = pinecone.Index(os.getenv("PINECONE_INDEX", ""))

# Read the csv file with all the course data
dataframe = pd.read_csv("courses_data.csv")


# Preprocess the data
def preprocess(identifier):
    # Get the row in the dataframe that matches the identifier
    # Get the data from each row and store it in a variable. If the data is missing, set the value to "None"
    row = dataframe.loc[dataframe["identifier"] == identifier].iloc[0]
    title = row.title if row.title is not None else "None"
    professor = row.professor if row.professor is not None else "None"
    term = row.term if row.term is not None else "None"
    overall_course_mean = (
        row.overall_course_mean if not pd.isna(row.overall_course_mean) else "None"
    )
    overall_instructor_mean = (
        row.overall_instructor_mean
        if not pd.isna(row.overall_instructor_mean)
        else "None"
    )
    coursework_mean = (
        row.coursework_mean if not pd.isna(row.coursework_mean) else "None"
    )
    coursework_median = (
        row.coursework_median if not pd.isna(row.coursework_median) else "None"
    )
    coursework_mode = (
        row.coursework_mode if not pd.isna(row.coursework_mode) else "None"
    )
    coursework_stddev = (
        row.coursework_stddev if not pd.isna(row.coursework_stddev) else "None"
    )
    comments = row.comments if isinstance(row.comments, str) else "None"
    comment_sentiment = (
        row.comment_sentiment if not pd.isna(row.comment_sentiment) else "None"
    )

    # Limit the comments to 8000 characters
    comments = comments[:8000]
    # Cut the last comment if it is not complete
    comments = re.search(r"(.*),", comments)
    if comments:
        comments = comments.group(1) + ".']"
    else:
        comments = "None"

    # Create the text and metadata strings for the pinecone index. The text will be embedded and the metadata will be referred to when querying.
    text = f"{title} taught by {professor} in {term} with an overall course mean of {overall_course_mean}, an overall instructor mean of {overall_instructor_mean}, a coursework mean of {coursework_mean}, a coursework median of {coursework_median}, a coursework mode of {coursework_mode}, and a coursework standard deviation of {coursework_stddev}. The comment sentiments are {comment_sentiment} and here are the comments: {comments}."

    metadata = {
        "title": title,
        "professor": professor,
        "term": term,
        "overall_course_mean": overall_course_mean,
        "overall_instructor_mean": overall_instructor_mean,
        "coursework_mean": coursework_mean,
        "coursework_median": coursework_median,
        "coursework_mode": coursework_mode,
        "coursework_stddev": coursework_stddev,
        "comments": comments,
        "comment_sentiment": comment_sentiment,
    }

    return text, metadata


# Create a new metadata column in the dataframe
dataframe["metadata"] = None

# Loop through each identifier in the dataframe, preprocess it, and then update the text and metadata columns
for i, identifier in enumerate(dataframe["identifier"]):
    text, metadata = preprocess(identifier)
    dataframe.at[i, "text"] = text
    dataframe.at[i, "metadata"] = metadata


# Generate the embedding
def embedding(text):
    res = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return res.data[0].embedding


# Loop through each row in the dataframe and upload the embedding, metadata, and identifier to the pinecone index
for i in range(len(dataframe)):
    text = dataframe.at[i, "text"]
    embedding_vector = embedding(text)
    metadata = dataframe.at[i, "metadata"]

    title = dataframe.at[i, "title"]
    professor = dataframe.at[i, "professor"]
    term = dataframe.at[i, "term"]

    id_raw = f"{title} by {professor} in {term}"
    id = re.sub(r"[^\x00-\x7F]+", "_", id_raw)
    print(id)

    index.upsert([(id, embedding_vector, metadata)])
