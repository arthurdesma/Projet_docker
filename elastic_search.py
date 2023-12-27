from elasticsearch import helpers


def index_data_to_es(es, db, collection_name, index_name):
    collection = db[collection_name]
    docs = collection.find({})

    fields_to_include = []
    if collection_name == "grand_prix_results":
        fields_to_include = ["Grand Prix", "Winner", "Years", "Car"]
    elif collection_name == "driver_standings":
        fields_to_include = ["Driver name", "Grand Prix", "Years"]

    actions = []
    for doc in docs:
        mongo_id_str = str(doc["_id"])
        # Check if the document already exists in Elasticsearch
        if not document_exists(es, index_name, mongo_id_str):
            print(f"Indexing document with mongo_id: {mongo_id_str}")
            action = {
                "_index": index_name,
                "_id": mongo_id_str,  # Use mongo_id_str as the document ID in Elasticsearch
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
    try:
        return es.exists(index=index_name, id=document_id)
    except Exception as e:
        print(f"Error checking document existence: {e}")
        return False
