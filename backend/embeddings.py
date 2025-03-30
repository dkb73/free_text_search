import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import config 

# Configure Gemini API
genai.configure(api_key=config.GEMINI_API_KEY)  # Use env variable instead of hardcoding

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

# Fetch hostel data
hostels = list(hostel_collection.find({}))

# Debugging: Check if data exists
if not hostels:
    print("❌ No hostel data found in the database. Did you run db.py?")
    exit()

# Store MongoDB IDs alongside embeddings
hostel_ids = []
hostel_embeddings = []

for hostel in hostels:
    formatted_text = f"{hostel['name']} in {hostel['location']}. {hostel['description']} Facilities: {', '.join(hostel['facilities'])}. Room Types: {', '.join(hostel['room_types'])}. Rent: {hostel['monthly_rent']} INR. Gender: {hostel['gender']}."
    
    try:
        embedding = get_embedding(formatted_text)
        hostel_embeddings.append(embedding)
        hostel_ids.append(str(hostel["_id"]))  # Store _id as string
    except Exception as e:
        print(f"⚠️ Failed to generate embedding for {hostel['name']}: {e}")

# Convert embeddings to NumPy array
if not hostel_embeddings:
    print("❌ No embeddings generated. Check your Gemini API setup.")
    exit()

hostel_embeddings = np.array(hostel_embeddings, dtype="float32")

# Create FAISS index
index = faiss.IndexFlatL2(hostel_embeddings.shape[1])
index.add(hostel_embeddings)

# Save FAISS index and hostel_ids
faiss.write_index(index, "hostel_index.faiss")
np.save("hostel_ids.npy", np.array(hostel_ids))

print(f"✅ Stored embeddings for {len(hostels)} hostels.")
