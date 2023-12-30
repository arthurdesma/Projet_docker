from elasticsearch import helpers


def index_data_to_es(es, db, collection_name, index_name):
    """
    Indexes data from a MongoDB collection into an Elasticsearch index.

    Args:
    es: Elasticsearch client instance.
    db: MongoDB database instance.
    collection_name (str): The name of the MongoDB collection to index.
    index_name (str): The name of the Elasticsearch index.

    This function reads documents from the specified MongoDB collection, filters the fields based on the collection name,
    and then indexes them into Elasticsearch. It only indexes documents that do not already exist in Elasticsearch.
    """
    collection = db[collection_name]
    docs = collection.find({})

    fields_to_include = []
    if collection_name == "grand_prix_results":
        fields_to_include = ["Grand Prix", "Winner", "Year", "Car"]
    elif collection_name == "driver_standings":
        fields_to_include = ["Driver name", "Grand Prix", "Year"]

    actions = []
    for doc in docs:
        mongo_id_str = str(doc["_id"])
        if not document_exists(es, index_name, mongo_id_str):
            print(f"Indexing document with mongo_id: {mongo_id_str}")
            action = {
                "_index": index_name,
                "_id": mongo_id_str,
                "_source": {
                    "mongo_id": mongo_id_str,
                    **{k: v for k, v in doc.items() if k in fields_to_include},
                },
            }
            actions.append(action)

    if actions:
        success, failed = helpers.bulk(es, actions, stats_only=True)
        print(f"Successfully indexed {success} documents, {failed} failures")
    else:
        print("No new documents to index.")


def document_exists(es, index_name, document_id):
    """
    Checks if a document exists in an Elasticsearch index.

    Args:
    es: Elasticsearch client instance.
    index_name (str): The name of the Elasticsearch index.
    document_id (str): The ID of the document to check.

    Returns:
    bool: True if the document exists, False otherwise.

    This function checks the existence of a document in an Elasticsearch index by its ID.
    """
    try:
        return es.exists(index=index_name, id=document_id)
    except Exception as e:
        print(f"Error checking document existence: {e}")
        return False


def build_es_query_for_driver_standings(grand_prix, year):
    """
    Builds a search query for Elasticsearch based on the provided filters for driver standings.

    Args:
    grand_prix (str): The name of the Grand Prix to filter by.
    year (int): The year to filter by.

    Returns:
    dict: A dictionary representing the Elasticsearch query.

    This function constructs an Elasticsearch query to search for driver standings, filtered by Grand Prix and/or year.
    """
    query_filters = []

    if grand_prix:
        query_filters.append({"match": {"Grand Prix": grand_prix}})
    if year:
        query_filters.append({"match": {"Year": year}})

    if query_filters:
        search_query = {"query": {"bool": {"must": query_filters}}, "size": 100}
    else:
        search_query = {"query": {"match_all": {}}, "size": 100}

    return search_query


def build_es_query_for_grand_prix_results(year,Car,Winner):
    """
    Builds a search query for Elasticsearch for Grand Prix results.

    Args:
    year (int): The year to filter the results by.

    Returns:
    dict: A dictionary representing the Elasticsearch query.

    This function creates an Elasticsearch query to search for Grand Prix results, optionally filtered by year.
    """
    if year:
        search_query = {"query": {"match": {"Year": year}}, "size": 100}
    if year:
        search_query = {"query": {"match": {"Car": Car}}, "size": 100}    
    if year:
        search_query = {"query": {"match": {"Winner": Winner}}, "size": 100}

    else:
        search_query = {"query": {"match_all": {}}, "size": 100}

    return search_query
