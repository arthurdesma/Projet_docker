import requests
from bs4 import BeautifulSoup

# Function to fetch race links
def fetch_race_links(year):
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
            grand_prix = columns[1].get_text(strip=True)
            winner = columns[3].get_text(strip=True)
            car = columns[4].get_text(strip=True)
            laps = columns[5].get_text(strip=True)
            time = columns[6].get_text(strip=True)

            race_table.append({
                "Grand Prix": grand_prix,
                "Winner": winner,
                "Car": car,
                "Laps": laps,
                "Time": time,
                "Year": year,
            })

        return race_table

    except requests.exceptions.Timeout:
        return f"Request timed out for year {year}"
    except Exception as e:
        return f"An error occurred: {e}"



# Function to get race number result
def race_number(year, race):
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
            pos = columns[1].get_text(strip=True)
            no = columns[2].get_text(strip=True)
            driver = columns[3].get_text(strip=True)
            laps = columns[5].get_text(strip=True)
            time = columns[6].get_text(strip=True)
            pts = columns[7].get_text(strip=True)

            race_table.append({
                "Position": pos,
                "Numero pilot": no,
                "Driver name": driver,
                "Laps": laps,
                "Time": time,
                "Points": pts,
                "Grand Prix": race.split("/")[-1],
                "Year": year,
            })

        return race_table

    except requests.exceptions.Timeout:
        return f"Request timed out for year {year}, race {race}"
    except Exception as e:
        return f"An error occurred: {e}"
