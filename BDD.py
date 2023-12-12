from pymongo import MongoClient

def connect_db(db_name, collection_name):
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    collection = db[collection_name]
    return collection

def data_exists(collection, query):
    return collection.find_one(query) is not None

def insert_data_if_not_exists(collection, data, query_fields):
    for record in data:
        # Create a query based on the specified fields
        query = {field: record[field] for field in query_fields if field in record}
        if not data_exists(collection, query):
            collection.insert_one(record)
        else:
            print(f"Data already exists for {query}")
