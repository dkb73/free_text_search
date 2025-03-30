from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://your-app.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure Gemini API
GEMINI_API_KEY = str(os.getenv('GEMINI_API_KEY', '')).strip()
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY is required")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    raise

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI', "mongodb://localhost:27017/"))
db = client["hostelDB"]
hostel_collection = db["hostels"]

# Load FAISS index and hostel IDs
try:
    index = faiss.read_index("hostel_index.faiss")
    hostel_ids = np.load("hostel_ids.npy")
    logger.info("FAISS index and hostel IDs loaded successfully")
except Exception as e:
    logger.error(f"Error loading FAISS index or hostel IDs: {e}")
    index = None
    hostel_ids = None

# Function to generate embeddings
def get_embedding(text):
    try:
        logger.info(f"Generating embedding for query: {text}")
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        embedding = np.array(response["embedding"], dtype="float32")
        logger.info("Embedding generated successfully")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

@app.route("/api/search", methods=["POST"])
def search():
    if not index or hostel_ids is None:
        logger.error("FAISS index not available")
        return jsonify({"error": "Search system not properly initialized"}), 500

    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    # Get embedding for query
    query_embedding = get_embedding(query)
    if query_embedding is None:
        return jsonify({"error": "Failed to generate query embedding. Please try again."}), 500

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
    app.run(host="0.0.0.0", port=5000, debug=True) 