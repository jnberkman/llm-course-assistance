## courses.py

In this file, the objective is to take the raw html files of the QReports from Spring 2023 and Fall 2022 and organize them in a csv file. Beautiful soup is used at first to parse the html, then each a tag is found and within it, regex is used to extract the class code, title, professor, link, id, and term. Pandas is then used to create a dataframe and then a unique, but easily recognizable identifier is assigned to each row. The dataframes for the two semesters are concatenated then duplicates are removed and the dataframe is turned into courses.csv.

## course_data.py

In this file, the objective is to go to every class's unique qguide site, and organize the data on it. First, the logging is set up for downloading all of the course links from courses.csv and the links are then scraped from the csv. A directory is then created to store the raw html files and then they are downloaded. Joblib is used to allow multiple threads to download these links so it is faster and tqdm is used to display a progress bar. Once the html files are all downloaded, nltk's vader_lexicon is used to quantify the sentiment of the comments for each class. After all of the data is then organized using xml to target certain parts of the html pages and a dataframe is created that stores the more in-depth data about each course.

# embeddings.py

In this file, to give context to the LLM, embeddings are used. Pinecone is used as the vector database and the data is processed into a long string that can be vectorized as well as the associated metadata. A dataframe is then created for easier storage and the data is turned into an embedding using openai's text-embedding-ada-002 model. These embeddings are then uploaded to the database.

## query.py

In this file, the interaction with the LLM happens. First there is logging in the terminal and the request for the user's prompt. The user's prompt is then turned into a vector using openai's model so a proximity search can be conducted. Essentially, the vectorized prompt is then used as a query to find the most similar vectors, and then the metadata of the 5 (top_k=5) most similar vectors is used as context for the prompt to gpt-3.5-16k. The system instruction is given as well as the contextualized prompt and then the output of that is what the user sees.

## requirements.txt

Lists requirements for pip to install.
