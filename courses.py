import re

import pandas as pd
from bs4 import BeautifulSoup as bs


# Function to scrape data
def scrape(term):
    # Open the html file
    with open("./raw_data/courses/QReport_" + term + ".html", "r") as f:
        soup = bs(f, "html.parser")

    # Create empty list to store rows of data
    rows = []

    # Loop through the 'a' tags in the html file
    for link in soup.find_all("a"):
        # Only have links with 'bluera' in it
        if "bluera" not in link.get("href"):
            continue
        split = " ".join(link.get_text().split())
        # Extract course code
        code = re.search(r"^\w+(?:-\w+)?\s*\d+\w?", split)
        if code:
            code = code.group(0)
        else:
            continue

        # Extract course title
        title = re.search(r"(?<=-).+?(?=\s*\(\w+)", split)
        if title:
            title = title.group(0)
        else:
            continue

        # Extract professor
        professor = re.search(r"\(([^)]+)\)$", split)
        if professor:
            professor = professor.group(1)
        else:
            continue
        # Create row and append to list
        row = [code, title, professor, link.get("href"), link.get("id"), term]
        rows.append(row)

    # Create dataframe with list of rows
    dataframe = pd.DataFrame(
        rows, columns=["code", "title", "professor", "link", "id", "term"]
    )

    # Create the unique, legible identifier
    dataframe["identifier"] = (
        dataframe["code"]
        + "_"
        + dataframe["title"]
        + "("
        + dataframe["professor"]
        + ")"
        + "_"
        + dataframe["term"]
    )

    return dataframe


# Scrape the two terms and concatenate them
f2022 = scrape("f2022")
s2023 = scrape("s2023")
courses = pd.concat([f2022, s2023])
# Drop the duplicates and then turn the dataframe into a csv
courses = courses.drop_duplicates(["identifier"])
courses.to_csv("courses.csv", index=False)
