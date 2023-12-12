import requests
from bs4 import BeautifulSoup
from BDD import connect_db, insert_data_if_not_exists


def fetch_race_links(year):
    url = f"https://www.formula1.com/en/results.html/{year}/races.html"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Failed to fetch data for year {year}: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.find_all(
        lambda tag: tag.name == "a"
        and "resultsarchive-filter-item-link" in tag.get("class", [])
        and tag.get("data-name") == "meetingKey"
    )

    race_data = []
    for element in items:
        data_value = element.get("data-value")
        if data_value:
            href = "https://www.formula1.com" + element.get("href")
            race_data.append({"year": year, "data_value": data_value, "href": href})

    return race_data


def year_result(year):
    url = f"https://www.formula1.com/en/results.html/{year}/races.html"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Failed to fetch data for year {year}: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="resultsarchive-table")

    # Initialize an empty list to hold the race data
    race_table = []

    # Iterate over each row in the table body
    for row in table.find_all("tr")[1:]:  # [1:] skips the header row
        columns = row.find_all("td")

        # Extract data from the relevant columns
        grand_prix = columns[1].get_text(strip=True)
        winner = columns[3].get_text(strip=True)
        car = columns[4].get_text(strip=True)
        laps = columns[5].get_text(strip=True)
        time = columns[6].get_text(strip=True)

        # Add the data to the race_data list
        race_table.append(
            {
                "Grand Prix": grand_prix,
                "Winner": winner,
                "Car": car,
                "Laps": laps,
                "Time": time,
                "Years": year
            }
        )

    # Now race_data contains all the extracted information
    return(race_table)


def race_number(year,race):
    url = (
        f"https://www.formula1.com/en/results.html/{year}/races/{race} race-result.html"
    )
    response = requests.get(url)

    if response.status_code != 200:
        return f"Failed to fetch data for year {year}: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="resultsarchive-table")

    # Initialize an empty list to hold the race data
    race_table = []

    # Iterate over each row in the table body
    for row in table.find_all("tr")[1:]:  # [1:] skips the header row
        columns = row.find_all("td")

        # Extract data from the relevant columns
        Pos = columns[1].get_text(strip=True)
        No = columns[2].get_text(strip=True)
        Driver = columns[3].get_text(strip=True)
        laps = columns[5].get_text(strip=True)
        time = columns[6].get_text(strip=True)
        Pts = columns[7].get_text(strip=True)

        # Add the data to the race_data list
        race_table.append(
            {
                "Position": Pos,
                "Numero pilot": No,
                "Driver name": Driver,
                "Laps": laps,
                "Time": time,
                "Points": Pts,
                "Grand Prix": race.split('/')[-1],
                "Years": year
            }
        )

    # Now race_data contains all the extracted information
    return(race_table)


all_race_data = []
for year in range(1950, 1951):
    race_links = fetch_race_links(year)
    if isinstance(race_links, list):  # Check if the returned value is a list
        all_race_data.extend(race_links)
    else:
        print(race_links)  # Print error message


# Now you can process all_race_data as needed
# for race in all_race_data:
#     print(race["year"], race["data_value"], race["href"])

# Specify database names
# Database and collection names
database_name = 'racing_database'
collection_name_1 = 'grand_prix_results'
collection_name_2 = 'driver_standings'

# Connect to collections
collection_1 = connect_db(database_name, collection_name_1)
collection_2 = connect_db(database_name, collection_name_2)

# Process data for the first collection
for year in range(1950, 1951):
    year_result_data = year_result(year)
    insert_data_if_not_exists(collection_1, year_result_data, ['Grand Prix', 'Winner','Car','Laps','Time','Years'])

# Process data for the second collection
for race in all_race_data:
    result_data = race_number(race["year"], race["data_value"])
    # Specify the fields to check for existing data in collection_2
    insert_data_if_not_exists(collection_2, result_data, ['Numero pilot', 'Driver name','Position','Laps','Time','Points','Grand Prix','Years'])

print("finish")