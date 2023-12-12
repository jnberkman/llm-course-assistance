import os

import pinecone
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Print the title and ask the user for their prompt
print(
    "\033[1m\033[4m\033[95m"
    + "Harvard Course Advisor (Beta) by Nathaniel Berkman"
    + "\033[0m\n"
)
prompt = input("Enter prompt: ")
print("\033[32m" + "----------------------------" + "\033[0m\n")

# Initialize pinecone
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY", ""),
    environment=os.getenv("PINECONE_ENVIRONMENT", ""),
)
index = pinecone.Index(os.getenv("PINECONE_INDEX", ""))

# Create an embedding of the prompt
res = client.embeddings.create(input=[prompt], model="text-embedding-ada-002")
embedding = res.data[0].embedding

# Query the pinecone database with the embedded prompt for similar vectors
results = index.query(embedding, top_k=5, include_metadata=True)

# Inject the results into the prompt
prompt = f"User Input: {prompt} \n Context: {results}"

# Generate a response from the prompt and give a system command. If there is no error, print the output from gpt-3.5-turbo-16k.
try:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": "You are an advisor to a student at Harvard University who helps give them information about classes. Use the context given to you in the prompt after Context: to inform your answer. In your response, please try to mention the course that you think is most relevant as well as the statistics associated with it like course mean, instructor mean, and coursework mean.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    print(completion.choices[0].message.content)
except OpenAIError or Exception as e:
    print(f"Error: {e}")
