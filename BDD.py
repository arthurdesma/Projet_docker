from pymongo import MongoClient
from elasticsearch import helpers

def connect_db(db_name, collection_name):
    """
    Connects to a MongoDB database and returns a collection.

    Args:
    db_name (str): The name of the database to connect to.
    collection_name (str): The name of the collection to access.

    Returns:
    Collection: A MongoDB collection object.

    This function establishes a connection to a MongoDB instance on the localhost and returns the specified collection
    from the specified database. It's used for database operations like querying and inserting data.
    """
    client = MongoClient("localhost", 27017)
    db = client[db_name]
    collection = db[collection_name]
    return collection


def data_exists(collection, query):
    """
    Checks if data exists in a MongoDB collection based on a query.

    Args:
    collection: The MongoDB collection to search in.
    query (dict): The query used to search in the collection.

    Returns:
    bool: True if data exists that matches the query, False otherwise.

    This function checks if there is at least one document in the collection that matches the given query.
    It is used to prevent duplicate entries in the database.
    """
    return collection.find_one(query) is not None


def insert_data_if_not_exists(collection, data, query_fields):
    """
    Inserts data into a MongoDB collection if it does not already exist.

    Args:
    collection: The MongoDB collection to insert data into.
    data (list of dict): The data to insert into the collection.
    query_fields (list of str): The fields to use in the query to check for existing data.

    This function iterates over a list of data, and for each element, it checks if a record already exists in the 
    collection with the specified fields. If the record does not exist, it inserts the new data into the collection.
    This is particularly useful for avoiding duplicate entries in the database.
    """
    for record in data:
        query = {field: record[field] for field in query_fields if field in record}
        if not data_exists(collection, query):
            collection.insert_one(record)
        else:
            print(f"Data already exists for {query}")
