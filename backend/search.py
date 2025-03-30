import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import config 

# Configure Gemini API
genai.configure(api_key=config.GEMINI_API_KEY)

# Function to generate embeddings
def get_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return np.array(response["embedding"], dtype="float32")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hostelDB"]
hostel_collection = db["hostels"]

# Load FAISS index and hostel IDs
index = faiss.read_index("hostel_index.faiss")
hostel_ids = np.load("hostel_ids.npy")

# User input
query = input("🔍 Enter hostel search query: ")
query_embedding = get_embedding(query).reshape(1, -1)

# Perform FAISS search
D, I = index.search(query_embedding, k=5)

# Debug FAISS output
print(f"FAISS Output - Distances: {D}, Indexes: {I}")

# Retrieve matching hostels from MongoDB
matching_hostels = []
for i in I[0]:
    if i < len(hostel_ids):  # Ensure valid index
        hostel_id = hostel_ids[i]
        hostel = hostel_collection.find_one({"_id": ObjectId(hostel_id)})
        if hostel:
            matching_hostels.append(hostel)

# Display results
if matching_hostels:
    print("\n🔹 **Top Matches:**")
    for hostel in matching_hostels:
        print(f"- {hostel['name']} ({hostel['location']}): {hostel['description']}")
else:
    print("❌ No matching hostels found.")
