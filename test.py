from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB URL
db = client.racing_database  # Replace with your database name

# Test collection and mongo_id
test_collection = "grand_prix_results"  # Replace with your collection name
test_mongo_id = "658c22bf3d8b08a02f3adb26"  # Replace with a valid mongo_id

# Fetch the document
mongo_doc = db[test_collection].find_one({'_id': ObjectId(test_mongo_id)})
print(mongo_doc)
