from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId
from dotenv import load_dotenv

# Explicitly load .env from the current working directory
load_dotenv(os.path.join(os.getcwd(), '.env'))

class DBService:
    def __init__(self, uri=None):
        self.uri = uri or os.getenv('MONGODB_URI')
        if not self.uri:
            # Fallback to the known Atlas URI if .env fails
            self.uri = "mongodb+srv://pritipatil8989:jupiter125@cluster0.f1jhvgq.mongodb.net/Plantdata?retryWrites=true&w=majority"
        elif "<db_password>" in self.uri:
            raise ValueError("Please replace '<db_password>' in your .env file with your actual MongoDB Atlas password.")
            
        print(f"DEBUG: Connecting to MongoDB at: {self.uri[:25]}...")
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
        self.db = self.client['Plantdata']
        
        # Indexes
        self.db.Diseases.create_index([('detected_at', -1)])
        self.db.Diseases.create_index([('disease_name', 1)])

    def save_detection(self, detection_data: dict) -> str:
        detection_data['detected_at'] = datetime.utcnow()
        result = self.db.Diseases.insert_one(detection_data)
        return str(result.inserted_id)

    def get_detection_history(self, limit=20, plant_filter=None, user_id=None) -> list:
        query = {}
        if plant_filter:
            query['disease_name'] = {'$regex': plant_filter, '$options': 'i'}
        if user_id:
            query['user_id'] = user_id
            
        cursor = self.db.Diseases.find(query).sort('detected_at', -1).limit(limit)
        history = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            history.append(doc)
        return history

    def get_disease_stats(self) -> list:
        pipeline = [
            {'$group': {'_id': '$disease_name', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        return list(self.db.detections.aggregate(pipeline))

    def seed_disease_catalog(self, class_names: list):
        for idx, name in enumerate(class_names):
            self.db.disease_catalog.update_one(
                {'disease_name': name},
                {'$set': {'class_index': idx, 'created_at': datetime.utcnow()}},
                upsert=True
            )

# Global instance
db_service = DBService()
