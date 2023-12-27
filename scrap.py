import requests
from bs4 import BeautifulSoup


# Function to fetch race links for a specific year from the Formula 1 website
def fetch_race_links(year):
    """
    Fetches links to race details for a specific year from the Formula 1 website.

    Args:
    year (int): The year for which to fetch race links.

    Returns:
    list: A list of dictionaries containing race data for the specified year.
          Each dictionary includes the year, data value, and the hyperlink to the race details.
          If there's an error or timeout, it returns an error message string.
    """
    try:
        print(f"Attempting to connect to URL for year {year}")
        url = f"https://www.formula1.com/en/results.html/{year}/races.html"
        response = requests.get(url, timeout=10)
        print("Connection attempt complete.")  # Debug message

        if response.status_code != 200:
            return f"Failed to fetch data for year {year}: HTTP Status Code {response.status_code}"

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

    except requests.exceptions.Timeout:
        return f"Request timed out for year {year}"
    except Exception as e:
        return f"An error occurred: {e}"


# Function to get year result
def year_result(year):
    """
    Fetches and parses the race results for a specific year from the Formula 1 website.

    Args:
    year (int): The year for which to fetch race results.

    Returns:
    list: A list of dictionaries containing details of each race for the specified year.
          Each dictionary includes race details like Grand Prix, Winner, Car, Laps, Time.
          If there's an error or timeout, it returns an error message string.
    """
    try:
        print(f"Attempting to connect to URL for year {year}...")
        url = f"https://www.formula1.com/en/results.html/{year}/races.html"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            return f"Failed to fetch data for year {year}: HTTP Status Code {response.status_code}"

        print(f"Successfully connected for year {year}.")
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", class_="resultsarchive-table")
        if table is None:
            return f"No data found for year {year}"

        race_table = []
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            race_table.append(
                {
                    "Grand Prix": columns[1].get_text(strip=True),
                    "Winner": columns[3].get_text(strip=True),
                    "Car": columns[4].get_text(strip=True),
                    "Laps": columns[5].get_text(strip=True),
                    "Time": columns[6].get_text(strip=True),
                    "Year": year,
                }
            )

        return race_table

    except requests.exceptions.Timeout:
        return f"Request timed out for year {year}"
    except Exception as e:
        return f"An error occurred: {e}"


# Function to get race number result
def race_number(year, race):
    """
    Fetches and parses the results of a specific race in a given year from the Formula 1 website.

    Args:
    year (int): The year of the race.
    race (str): The specific race (identified by a number or unique identifier) for which to fetch results.

    Returns:
    list: A list of dictionaries containing detailed results of the specified race.
          Each dictionary includes details like Position, Pilot Number, Driver Name, Laps, Time, Points.
          If there's an error or timeout, it returns an error message string.
    """
    try:
        print(f"Attempting to connect to URL for year {year}, race {race}...")
        url = f"https://www.formula1.com/en/results.html/{year}/races/{race}/race-result.html"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            return f"Failed to fetch data for year {year}, race {race}: HTTP Status Code {response.status_code}"

        print(f"Successfully connected for year {year}, race {race}.")
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", class_="resultsarchive-table")
        if table is None:
            return f"No data found for year {year} and race {race}"

        race_table = []
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            race_table.append(
                {
                    "Position": columns[1].get_text(strip=True),
                    "Numero pilot": columns[2].get_text(strip=True),
                    "Driver name": columns[3].get_text(strip=True),
                    "Laps": columns[5].get_text(strip=True),
                    "Time": columns[6].get_text(strip=True),
                    "Points": columns[7].get_text(strip=True),
                    "Grand Prix": race.split("/")[-1],
                    "Year": year,
                }
            )

        return race_table

    except requests.exceptions.Timeout:
        return f"Request timed out for year {year}, race {race}"
    except Exception as e:
        return f"An error occurred: {e}"
