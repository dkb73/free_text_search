# db.py

from pymongo import MongoClient
import config

# Connect to MongoDB
client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
hostel_collection = db[config.COLLECTION_NAME]

# Insert sample hostels if not present
def insert_sample_data():
    if hostel_collection.count_documents({}) == 0:
        sample_hostels = [
            {
                "name": "Elegant Girls PG",
                "location": "Kolkata, West Bengal",
                "description": "Well-maintained girls PG with comfortable rooms, food, and all necessary amenities.",
                "facilities": ["WiFi", "Mess", "Housekeeping", "CCTV", "Study Room"],
                "room_types": ["Single", "Double"],
                "monthly_rent": 11000,
                "ratings": 4.5,
                "reviews": 120,
                "gender": "Female",
                "distance_from_college": 1.8,
                "contact": {"name": "Mrs. Banerjee", "phone": "+919812345678"}
            },
            {
                "name": "Sunrise Boys Hostel",
                "location": "Mumbai, Maharashtra",
                "description": "Affordable hostel with WiFi, laundry, and AC rooms.",
                "facilities": ["WiFi", "Mess", "Laundry", "AC"],
                "room_types": ["Single", "Double"],
                "monthly_rent": 12000,
                "ratings": 4.3,
                "reviews": 95,
                "gender": "Male",
                "distance_from_college": 2.0,
                "contact": {"name": "Mr. Sharma", "phone": "+919876543211"}
            }
        ]
        hostel_collection.insert_many(sample_hostels)
        print("✅ Sample data inserted.")

# Run only if executed directly
if __name__ == "__main__":
    insert_sample_data()
