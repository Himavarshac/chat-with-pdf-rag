import requests
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import pipeline  # Add this import

# Define the function to crawl and scrape the website
def crawl_and_scrape(url):
    """
    Scrape and extract text from the given URL with a User-Agent header.
    Args:
        url (str): The URL of the website to scrape.
    Returns:
        str: Extracted text from the website.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Send GET request with the User-Agent header
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the website. Status code: {response.status_code}")
        return ""
    
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    
    return text

# Step 2: Function to split text into chunks
def split_text_into_chunks(text, chunk_size=500, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    return chunks

# Step 3: Generate embeddings (use SentenceTransformer or another embedding method)
def generate_openai_embeddings(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Replace with your preferred model
    return model.encode(chunks, show_progress_bar=True)

# Step 4: Store embeddings in ChromaDB
def store_embeddings_in_chromadb(chunks, embeddings):
    client = chromadb.Client()
    collection = client.create_collection(name="website_data")
    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"chunk_{i}"],
            documents=[chunk],
            embeddings=[embeddings[i]]
        )
    print("Data stored in ChromaDB!")

# Step 5: Retrieve relevant chunks from ChromaDB
def retrieve_relevant_chunks(query, collection):
    query_embedding = generate_openai_embeddings([query])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3  # Retrieve top 3 relevant chunks
    )
    return results["documents"]

# Step 6: Generate a response based on the relevant chunks
def generate_response(query, relevant_chunks):
    """
    Generate a response using an LLM.
    Args:
        query (str): User's query.
        relevant_chunks (list): Relevant chunks retrieved from the vector database.
    Returns:
        str: Generated response.
    """
    # Flatten the relevant_chunks list if it contains sublists
    flattened_chunks = [item for sublist in relevant_chunks for item in (sublist if isinstance(sublist, list) else [sublist])]

    # Join the relevant chunks as context
    context = "\n\n".join(flattened_chunks)
    
    prompt = f"Answer the following question based on the context:\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    
    # Use a local language model (e.g., GPT-2) for generating the response
    generator = pipeline("text-generation", model="gpt2")
    response = generator(prompt, max_length=300, num_return_sequences=1)
    
    return response[0]['generated_text']

# Final function to integrate all steps
def chat_with_website(url, query):
    # Step 1: Crawl and scrape website
    text = crawl_and_scrape(url)
    
    if not text:
        return "Failed to retrieve content from the website."
    
    # Step 2: Split text into chunks
    chunks = split_text_into_chunks(text)
    
    # Step 3: Filter chunks based on keywords like 'mission', 'purpose', etc.
    relevant_chunks = [chunk for chunk in chunks if 'mission' in chunk or 'purpose' in chunk]
    
    # If no relevant chunks are found, use all chunks
    if not relevant_chunks:
        relevant_chunks = chunks
    
    # Step 4: Generate embeddings for the chunks
    embeddings = generate_openai_embeddings(relevant_chunks)
    
    # Step 5: Store the chunks and embeddings in ChromaDB
    store_embeddings_in_chromadb(relevant_chunks, embeddings)
    
    # Step 6: Retrieve relevant chunks for the query
    client = chromadb.Client()
    collection = client.get_collection(name="website_data")
    relevant_chunks_from_db = retrieve_relevant_chunks(query, collection)
    
    # Step 7: Generate a response
    return generate_response(query, relevant_chunks_from_db)

# Example usage
url = "https://www.uchicago.edu/"
query = "What is this website about?"
response = chat_with_website(url, query)
print(response)