from fastapi import FastAPI, Request
from elasticsearch import Elasticsearch, helpers
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from fastapi import BackgroundTasks
from fastapi import FastAPI, Query
from elasticsearch import Elasticsearch
from bson import ObjectId


from BDD import connect_db, insert_data_if_not_exists
from scrap import fetch_race_links, year_result, race_number

app = FastAPI()
es = Elasticsearch("http://localhost:9200")

# Database configuration
database_name = "racing_database"
collection_name_1 = "grand_prix_results"
collection_name_2 = "driver_standings"

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client[database_name]


# Serve static files and templates
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    if not es.ping():
        raise ValueError("Cannot connect to Elasticsearch.")
    print("Connected to Elasticsearch!")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/update_database/")
async def update_database(start_year: int, end_year: int):
    end_year += 1
    all_race_data = []
    for year in range(start_year, end_year):
        race_links = fetch_race_links(year)
        if isinstance(race_links, list):
            all_race_data.extend(race_links)
        else:
            print(race_links)

    collection_1 = connect_db(database_name, collection_name_1)
    collection_2 = connect_db(database_name, collection_name_2)

    # Prepare and index data for collection 1
    for year in range(start_year, end_year):
        year_result_data = year_result(year)
        insert_data_if_not_exists(
            collection_1,
            year_result_data,
            ["Grand Prix", "Winner", "Car", "Laps", "Time", "Years"],
        )

    # Prepare and index data for collection 2
    for race in all_race_data:
        result_data = race_number(race["year"], race["data_value"])
        insert_data_if_not_exists(
            collection_2,
            result_data,
            [
                "Numero pilot",
                "Driver name",
                "Position",
                "Laps",
                "Time",
                "Points",
                "Grand Prix",
                "Years",
            ],
        )

@app.post("/update_and_index/")
async def update_and_index_database(background_tasks: BackgroundTasks, start_year: int, end_year: int):
    # Update the database
    await update_database(start_year, end_year)

    # Add indexing to background tasks
    background_tasks.add_task(index_data)

    return {"message": "Database update initiated and indexing scheduled"}


def index_data_to_es(collection_name, index_name):
    collection = db[collection_name]
    docs = collection.find({})
    actions = [
        {
            "_index": index_name,
            "_source": {
                'mongo_id': str(doc['_id']),  # Rename '_id' to 'mongo_id'
                **{k: v for k, v in doc.items() if k != '_id'}  # Exclude the original '_id'
            },
        }
        for doc in docs
    ]
    success, failed = helpers.bulk(es, actions, stats_only=True)
    print(f"Successfully indexed {success} documents, {failed} failures")



@app.post("/index_data/")
async def index_data():
    try:
        index_data_to_es(collection_name_1, "grand_prix_results_index")
        index_data_to_es(collection_name_2, "driver_standings_index")
        return {"message": "Data indexed successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/search/")
async def search_data(index: str, query: str = Query(None), size: int = 10):
    """
    Search data in the specified Elasticsearch index.

    Args:
    - index (str): The name of the Elasticsearch index to search.
    - query (str, optional): The search query. Defaults to None, which fetches all documents.
    - size (int, optional): Number of results to return. Defaults to 10.

    Returns:
    - dict: The search results from Elasticsearch.
    """
    if not query:
        # Match all documents if no query is provided
        search_query = {"query": {"match_all": {}}}
    else:
        # Use a simple text query for the provided search term
        search_query = {"query": {"simple_query_string": {"query": query}}}

    try:
        response = es.search(index=index, body=search_query, size=size)
        return {"status": "success", "data": response['hits']['hits']}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/list_indices/")
async def list_indices():
    try:
        response = es.cat.indices(format="json")
        return {"status": "success", "indices": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
