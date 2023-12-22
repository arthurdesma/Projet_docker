import requests
from bs4 import BeautifulSoup

# Function to fetch race links
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


print(fetch_race_links(2023))
# Function to get year result

def year_result(year):
    url = f"https://www.formula1.com/en/results.html/{year}/races.html"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Failed to fetch data for year {year}: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="resultsarchive-table")

    race_table = []

    for row in table.find_all("tr")[1:]:
        columns = row.find_all("td")

        grand_prix = columns[1].get_text(strip=True)
        winner = columns[3].get_text(strip=True)
        car = columns[4].get_text(strip=True)
        laps = columns[5].get_text(strip=True)
        time = columns[6].get_text(strip=True)

        race_table.append(
            {
                "Grand Prix": grand_prix,
                "Winner": winner,
                "Car": car,
                "Laps": laps,
                "Time": time,
                "Years": year,
            }
        )

    return race_table

# print(year_result(2023))

# Function to get race number result
def race_number(year, race):
    url = (
        f"https://www.formula1.com/en/results.html/{year}/races/{race}/race-result.html"
    )
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for year {year}: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="resultsarchive-table")

    # Skip if the table is not found
    if table is None:
        print(f"No data found for year {year} and race {race}")
        return []

    race_table = []
    for row in table.find_all("tr")[1:]:
        columns = row.find_all("td")

        Pos = columns[1].get_text(strip=True)
        No = columns[2].get_text(strip=True)
        Driver = columns[3].get_text(strip=True)
        laps = columns[5].get_text(strip=True)
        time = columns[6].get_text(strip=True)
        Pts = columns[7].get_text(strip=True)

        race_table.append(
            {
                "Position": Pos,
                "Numero pilot": No,
                "Driver name": Driver,
                "Laps": laps,
                "Time": time,
                "Points": Pts,
                "Grand Prix": race.split("/")[-1],
                "Years": year,
            }
        )

    return race_table