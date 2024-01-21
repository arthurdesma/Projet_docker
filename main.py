from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson import ObjectId, json_util
from fastapi.responses import FileResponse
import os


from mongoDB_folder.MongoDB import connect_db, insert_data_if_not_exists
from scraping_folder.scrap import fetch_race_links, year_result, race_number
from elastic_search_folder.elastic_search import index_data_to_es, build_es_query_for_driver_standings, build_es_query_for_grand_prix_results
from data_vis.data import save_grand_prix_winners_chart

# Initialize the FastAPI application
app = FastAPI()

# Initialize Elasticsearch client
es = Elasticsearch("http://elasticsearch:9200")

# Database configuration
database_name = "racing_database"
collection_name_1 = "grand_prix_results"
collection_name_2 = "driver_standings"

# Initialize MongoDB client
mongo_client = MongoClient("mongodb://mongodb:27017")
db = mongo_client[database_name]

# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """
    Function to be executed at the application startup.
    Checks if Elasticsearch is running and connected.
    """
    if not es.ping():
        raise ValueError("Cannot connect to Elasticsearch.")
    print("Connected to Elasticsearch!")



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Endpoint to display the home page.
    Retrieves data from MongoDB and passes it to the template.
    """
    collection_1 = db["grand_prix_results"]
    collection_2 = db["driver_standings"]

    data_1 = list(collection_1.find({}))
    data_2 = list(collection_2.find({}))

    return templates.TemplateResponse(
        "home.html", {"request": request, "data_1": data_1, "data_2": data_2}
    )


@app.post("/update_database/")
async def update_database(start_year: int, end_year: int):
    """
    Endpoint to update the racing database.
    Fetches and stores data for specified years in MongoDB.
    """
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

    for year in range(start_year, end_year):
        year_result_data = year_result(year)
        insert_data_if_not_exists(
            collection_1,
            year_result_data,
            ["Grand Prix", "Winner", "Car", "Laps", "Time", "Years"],
        )

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
async def update_and_index_database(
    background_tasks: BackgroundTasks, start_year: int, end_year: int
):
    """
    Endpoint to update the database and schedule data indexing.
    Initiates database update and adds indexing to background tasks.
    """
    await update_database(start_year, end_year)
    background_tasks.add_task(index_data)

    return {"message": "Database update initiated and indexing scheduled"}


@app.post("/index_data/")
async def index_data():
    """
    Endpoint to index data from MongoDB to Elasticsearch.
    Enhances the search capabilities by indexing the data.
    """
    try:
        index_data_to_es(es, db, collection_name_1, "grand_prix_results")
        index_data_to_es(es, db, collection_name_2, "driver_standings")
        return {"message": "Data indexed successfully"}
    except Exception as e:
        return {"error": str(e)}


async def perform_search(index, query):
    """
    Helper function to perform a search query in Elasticsearch.
    Retrieves corresponding MongoDB documents based on Elasticsearch hits.
    """
    try:
        response = es.search(index=index, body=query)
        es_hits = response["hits"]["hits"]
    except Exception as e:
        return {"status": "error", "message": f"Elasticsearch query failed: {str(e)}"}

    mongo_docs = []
    for hit in es_hits:
        mongo_id = hit["_source"].get("mongo_id")
        if mongo_id:
            try:
                mongo_doc = db[index].find_one({"_id": ObjectId(mongo_id)})
                if mongo_doc:
                    mongo_doc_dict = json_util._json_convert(mongo_doc)
                    mongo_doc_dict["_id"] = str(mongo_doc_dict["_id"])
                    mongo_docs.append(mongo_doc_dict)
                else:
                    mongo_docs.append(
                        {"error": "MongoDB document not found", "mongo_id": mongo_id}
                    )
            except Exception as e:
                mongo_docs.append({"error": str(e), "mongo_id": mongo_id})
        else:
            mongo_docs.append(
                {"error": "Missing mongo_id in Elasticsearch hit", "hit": hit}
            )

    return {"status": "success", "data": mongo_docs}


@app.get("/list_indices/")
async def list_indices():
    """
    Endpoint to list all indices in Elasticsearch.
    Useful for administrative and debugging purposes.
    """
    try:
        response = es.cat.indices(format="json")
        return {"status": "success", "indices": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/search/driver_standings/")
async def search_driver_standings(grand_prix: str = None, year: int = None):
    """
    Endpoint to search for driver standings.
    Accepts parameters for grand prix and year to refine the search.
    """
    es_query = build_es_query_for_driver_standings(grand_prix, year)
    return await perform_search("driver_standings", es_query)


@app.get("/search/grand_prix_results/")
async def search_grand_prix_results(year: int = None, Car: str = None, Winner: str = None):
    """
    Endpoint to search for Grand Prix results.
    Accepts a parameter for the year to refine the search.
    """
    es_query = build_es_query_for_grand_prix_results(year,Car,Winner)
    return await perform_search("grand_prix_results", es_query)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)