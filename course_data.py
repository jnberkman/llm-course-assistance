# This file will take a long time to run

import logging
import os

import nltk
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from joblib import Parallel, delayed
from lxml import etree
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm import tqdm

# Download vader_lexicon for sentiment analysis
nltk.download("vader_lexicon")


# Download course data
def download_course_data():
    # Setup loggging and preprocess the links from the csv created in courses.py
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    def preprocess_qlinks():
        dataframe = pd.read_csv("courses.csv")
        return [
            (url, code) for url, code in zip(dataframe["link"], dataframe["identifier"])
        ]

    PACKAGES = preprocess_qlinks()

    # Create directory to store the raw html files of each course
    os.makedirs("./raw_data/qguides", exist_ok=True)

    # Download the html files
    def load_url(session, package, retry=3):
        url, filename = package
        filename = filename.replace("/", "%2F")
        try:
            response = session.get(url, timeout=60)
            response.raise_for_status()
            with open(f"./raw_data/qguides/{filename}.html", "w") as f:
                f.write(response.text)
            return True
        except requests.RequestException as e:
            logging.warning(f"Error downloading {url}: {e}")
            if retry > 0:
                return load_url(session, package, retry - 1)
            else:
                return False

    # Enable multithreading
    threads = int(input("How many threads to use? (5-15): "))
    if threads not in range(5, 16):
        logging.error("Invalid number. Continuing with 5 threads.")
        threads = 5

    # Download the html files using the inputted number of threads
    with requests.Session() as session:
        results = Parallel(n_jobs=threads)(
            delayed(load_url)(session, package)
            for package in tqdm(PACKAGES, desc="Downloading")
        )

    success_count = sum(1 for result in results if result)
    logging.info(f"Downloaded {success_count}/{len(PACKAGES)} pages successfully.")


download_course_data()


# Perform sentiment analysis on the comments
def comment_sentiment(comment):
    if comment is None:
        return None
    else:
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(comment)
        return scores["compound"]


# Organize the course data into a dataframe
def organize_course_data(identifier):
    # Open each html file in the raw_data/qguides directory and parse it in xml format
    with open(f"./raw_data/qguides/{identifier}.html", "r") as f:
        soup = bs(f, "lxml")
        tree = etree.HTML(str(soup), parser=etree.HTMLParser())

    # Remove the encoding from the identifier, read courses.csv, and find the row with the matching identifier
    identifier = identifier.replace("%2F", "/")
    courses = pd.read_csv("courses.csv")
    course = courses.loc[courses["identifier"] == identifier]

    # Create a dictionary with the data from the html file
    rows = {
        "identifier": identifier,
        "id": course["id"].values[0],
        "code": identifier.split("_")[0],
        "title": course["title"].values[0],
        "professor": course["professor"].values[0],
        "term": course["term"].values[0],
        "overall_course_mean": None,
        "overall_instructor_mean": None,
        "coursework_mean": None,
        "coursework_median": None,
        "coursework_mode": None,
        "coursework_stddev": None,
        "comments": [],
        "comment_sentiment": [],
    }

    # Upload the dictionary with the data from each html file
    overall_course_mean = tree.xpath(
        "/html/body/article/div[3]/div[1]/table/tbody/tr[1]/td[7]"
    )
    if overall_course_mean:
        rows["overall_course_mean"] = str(
            round(float(overall_course_mean[0].text) / 5, 4)
        )
    else:
        rows["overall_course_mean"] = None

    overall_instructor_mean = tree.xpath(
        "/html/body/article/div[5]/div[1]/table/tbody/tr[1]/td[7]"
    )
    if overall_instructor_mean:
        if overall_instructor_mean[0].text == "NRP":
            rows["overall_instructor_mean"] = None
        else:
            rows["overall_instructor_mean"] = str(
                round(float(overall_instructor_mean[0].text) / 5, 4)
            )
    else:
        rows["overall_instructor_mean"] = None

    coursework_mean = tree.xpath(
        "/html/body/article/div[6]/div[2]/div/div[3]/table/tbody/tr[3]/td"
    )
    if coursework_mean:
        rows["coursework_mean"] = coursework_mean[0].text
    else:
        rows["coursework_mean"] = None

    coursework_median = tree.xpath(
        "/html/body/article/div[6]/div[2]/div/div[3]/table/tbody/tr[4]/td"
    )
    if coursework_median:
        rows["coursework_median"] = coursework_median[0].text
    else:
        rows["coursework_median"] = None

    coursework_mode = tree.xpath(
        "/html/body/article/div[6]/div[2]/div/div[3]/table/tbody/tr[5]/td"
    )
    if coursework_mode:
        rows["coursework_mode"] = coursework_mode[0].text
    else:
        rows["coursework_mode"] = None

    coursework_stddev = tree.xpath(
        "/html/body/article/div[6]/div[2]/div/div[3]/table/tbody/tr[6]/td"
    )
    if coursework_stddev:
        if coursework_stddev[0].text == "N/A":
            rows["coursework_stddev"] = None
        else:
            rows["coursework_stddev"] = coursework_stddev[0].text
    else:
        rows["coursework_stddev"] = None

    comments = [
        comment.xpath("string(.)").strip()
        for comment in tree.xpath(
            "/html/body/article/div[9]/div[2]/div[1]/table/tbody/tr/td"
        )
    ]
    if comments:
        rows["comments"] = comments
        rows["comment_sentiment"] = [comment_sentiment(comment) for comment in comments]
    else:
        rows["comments"] = None
        rows["comment_sentiment"] = None

    # Return the row data
    return rows


# Create an empty list to store the course data
courses_data = []
# Loop through each file in the raw_data/qguides directory and append the course data in each row to the list
for file in os.listdir("./raw_data/qguides"):
    if file.endswith(".html"):
        identifier = file[:-5]
        row = organize_course_data(identifier)
        if row is not None:
            courses_data.append(row)

# Create a dataframe with the course data and then turn it into a csv
dataframe = pd.DataFrame(courses_data)
dataframe.to_csv("courses_data.csv", index=False)
