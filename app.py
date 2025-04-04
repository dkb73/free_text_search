from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import config  

app = Flask(__name__)

# Configure Gemini API
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hostelDB"]
hostel_collection = db["hostels"]

# Load FAISS index and hostel IDs
try:
    index = faiss.read_index("hostel_index.faiss")
    hostel_ids = np.load("hostel_ids.npy")
except Exception as e:
    print(f"Error loading FAISS index or hostel IDs: {e}")
    index = None
    hostel_ids = None

# Function to generate embeddings
def get_embedding(text):
    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return np.array(response["embedding"], dtype="float32")
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")  # Serve the frontend page

@app.route("/search", methods=["POST"])
def search():
    if not index or hostel_ids is None:
        return jsonify({"error": "FAISS index not available"}), 500

    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    # Get embedding for query
    query_embedding = get_embedding(query)
    if query_embedding is None:
        return jsonify({"error": "Failed to generate query embedding"}), 500

    query_embedding = query_embedding.reshape(1, -1)

    # Search using FAISS
    D, I = index.search(query_embedding, k=5)

    # Handle case where no results are found
    if I[0][0] == -1:
        return jsonify({"message": "No matching hostels found"}), 200

    # Retrieve hostel details from MongoDB
    results = []
    for i in I[0]:
        if 0 <= i < len(hostel_ids):
            hostel_id = hostel_ids[i]
            hostel = hostel_collection.find_one({"_id": ObjectId(hostel_id)})

            if hostel:
                results.append({
                    "id": str(hostel["_id"]),
                    "name": hostel.get("name", "Unknown"),
                    "location": hostel.get("location", "Not specified"),
                    "description": hostel.get("description", "No description available"),
                    "facilities": hostel.get("facilities", []),
                    "room_types": hostel.get("room_types", []),
                    "monthly_rent": hostel.get("monthly_rent", "Not available"),
                    "ratings": hostel.get("ratings", "Not rated"),
                    "contact": hostel.get("contact", {}).get("phone", "Not provided")
                })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
