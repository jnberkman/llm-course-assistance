# Data-driven course assistance using LLMs

## Demo
https://youtu.be/HbhoDbdQyqc

## Walkthrough

Ensure that all files within the raw_data folder are downloaded. This is what the directory tree should look like:
```
.
└── raw_data
    ├── concentration_requirements
    ├── courses
    └── qguides
```

Next make sure Python is installed as well as pip. For my project I used Python version 3.11.6

Then install all the requirements doing
```bash
pip install -r requirements.txt
```
within the project directory

Configure the .env file for Pinecone and OpenAI usage.

The Pinecone index's dimensions should be 1536 using cosine and the pod type should be p2. 

Now execute courses.py using the play button in VSCode.

Once that is done running, a csv should be created.

Make sure to log into the QReports at https://qreports.fas.harvard.edu/
Once you have done that, execute course_data.py. This may take several minutes.

After that, if you do not want to use the API keys provided:
- Create an OpenAI api Key at https://platform.openai.com/api-keys
- Create an index named CS50 at https://app.pinecone.io/ and update the respective pinecone.init sections in embeddings.py and query.py

Next, execute embeddings.py. This may take several minutes.

Finally, execute query.py. This is the file that allows you to interact with the LLM.

--

If you would like to test out the GPT, check it out at:
https://chat.openai.com/g/g-TJqY9P17T-harvard-advisor