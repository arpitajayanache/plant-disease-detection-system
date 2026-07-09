from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId
from dotenv import load_dotenv

# Explicitly load .env from the root
load_dotenv(os.path.join(os.getcwd(), '.env'))

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    # Fallback to Atlas URI
    MONGODB_URI = "mongodb+srv://pritipatil8989:jupiter125@cluster0.f1jhvgq.mongodb.net/Plantdata?retryWrites=true&w=majority"
elif "<db_password>" in MONGODB_URI:
    raise ValueError("Please replace '<db_password>' in your .env file with your actual MongoDB Atlas password.")

print(f"DEBUG: Root db_service connecting to: {MONGODB_URI[:25]}...")
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client['Plantdata']

# Indexes
db.Diseases.create_index([('detected_at', -1)])
db.Diseases.create_index([('disease_name', 1)])

def save_detection(detection_data: dict) -> str:
    """Save a new detection result to the 'Diseases' collection."""
    if 'detected_at' not in detection_data:
        detection_data['detected_at'] = datetime.utcnow()
    result = db.Diseases.insert_one(detection_data)
    return str(result.inserted_id)

def get_detection_history(limit=20, plant_filter=None, user_id=None) -> list:
    """Retrieve detection history from the 'Diseases' collection."""
    query = {}
    if plant_filter:
        query['disease_name'] = {'$regex': plant_filter, '$options': 'i'}
    if user_id:
        query['user_id'] = user_id
        
    cursor = db.Diseases.find(query).sort('detected_at', -1).limit(limit)
    history = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        history.append(doc)
    return history

def seed_disease_catalog(class_names: list):
    """Seed catalog into Diseases collection (reference records)."""
    for idx, name in enumerate(class_names):
        db.Diseases.update_one(
            {'disease_name': name, 'is_catalog_entry': True},
            {'$set': {
                'class_index': idx, 
                'created_at': datetime.utcnow(),
                'is_catalog_entry': True
            }},
            upsert=True
        )

def get_disease_stats() -> list:
    pipeline = [
        {'$match': {'is_catalog_entry': {'$ne': True}}},
        {'$group': {'_id': '$disease_name', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    return list(db.Diseases.aggregate(pipeline))

def update_session(user_id: str, language: str):
    """Update user language preference in the users collection."""
    if not user_id: return
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'language': language, 'last_active': datetime.utcnow()}},
        upsert=False
    )
