from fastapi import FastAPI

# Assuming BDD.py contains the necessary database functions
from BDD import connect_db, insert_data_if_not_exists
from scrap import fetch_race_links, year_result, race_number

app = FastAPI()

# Database configuration
database_name = "racing_database"
collection_name_1 = "grand_prix_results"
collection_name_2 = "driver_standings"


@app.post("/update_database/")
def update_database(start_year: int, end_year: int):
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
