import requests
from bs4 import BeautifulSoup

def fetch_race_links(year):
    url = f"https://www.formula1.com/en/results.html/{year}/races.html"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Failed to fetch data for year {year}: {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')
    
    items = soup.find_all(
        lambda tag: 
        tag.name == "a" and 
        "resultsarchive-filter-item-link" in tag.get("class", []) and 
        tag.get("data-name") == "meetingKey"
    )

    race_data = []
    for element in items:
        data_value = element.get("data-value")
        if data_value:
            href = "https://www.formula1.com" + element.get("href")
            race_data.append({"year": year, "data_value": data_value, "href": href})

    return race_data

all_race_data = []
for year in range(1950, 2023):
    race_links = fetch_race_links(year)
    if isinstance(race_links, list):  # Check if the returned value is a list
        all_race_data.extend(race_links)
    else:
        print(race_links)  # Print error message

# Now you can process all_race_data as needed
for race in all_race_data:
    print(race['year'], race['data_value'], race['href'])