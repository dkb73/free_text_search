from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import google.generativeai as genai
import faiss
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
index = None
hostel_ids = None

def load_index_files():
    global index, hostel_ids
    try:
        # Get the absolute path to the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Current directory: {current_dir}")
        
        # Define possible locations for the files
        possible_locations = [
            os.path.join(current_dir, 'data'),  # data subdirectory (primary location)
            current_dir,  # Current directory (fallback)
        ]
        
        # Log all possible locations
        logger.info("Searching for files in the following locations:")
        for location in possible_locations:
            logger.info(f"- {location}")
            if os.path.exists(location):
                logger.info(f"  Directory exists: Yes")
                files = os.listdir(location)
                logger.info(f"  Files in directory: {files}")
            else:
                logger.info(f"  Directory exists: No")
        
        # Try each location until we find the files
        for location in possible_locations:
            index_path = os.path.join(location, "hostel_index.faiss")
            ids_path = os.path.join(location, "hostel_ids.npy")
            
            logger.info(f"\nAttempting to load files from: {location}")
            logger.info(f"Index path: {index_path}")
            logger.info(f"IDs path: {ids_path}")
            
            if os.path.exists(index_path) and os.path.exists(ids_path):
                logger.info(f"Found files in: {location}")
                logger.info(f"Index file size: {os.path.getsize(index_path)} bytes")
                logger.info(f"IDs file size: {os.path.getsize(ids_path)} bytes")
                
                index = faiss.read_index(index_path)
                hostel_ids = np.load(ids_path)
                logger.info("FAISS index and hostel IDs loaded successfully")
                return True
            else:
                logger.info("Files not found in this location")
                
        logger.error("Could not find index files in any of the expected locations")
        return False
    except Exception as e:
        logger.error(f"Error loading FAISS index or hostel IDs: {e}")
        logger.exception("Full traceback:")
        return False

# Load the index files
if not load_index_files():
    logger.error("Failed to load index files. The search system will not be available.")

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

class SearchQuery(BaseModel):
    query: str

@app.post("/api/search")
async def search(search_query: SearchQuery):
    if not index or hostel_ids is None:
        logger.error("FAISS index not available")
        raise HTTPException(status_code=500, detail="Search system not properly initialized. Please check server logs.")

    query = search_query.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Get embedding for query
    query_embedding = get_embedding(query)
    if query_embedding is None:
        raise HTTPException(status_code=500, detail="Failed to generate query embedding. Please try again.")

    query_embedding = query_embedding.reshape(1, -1)

    # Search using FAISS
    D, I = index.search(query_embedding, k=5)

    # Handle case where no results are found
    if I[0][0] == -1:
        return {"message": "No matching hostels found"}

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

    return results

@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 