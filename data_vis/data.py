import requests
import matplotlib.pyplot as plt
import os
import httpx


async def save_grand_prix_winners_chart(api_endpoint, image_path):
    async with httpx.AsyncClient() as client:
        response = await client.get(api_endpoint)

    if response.status_code != 200:
        print("Failed to fetch data from the API")
        return

    data = response.json()['data']

    win_counts = {}
    for item in data:
        winner = item['Winner']
        win_counts[winner] = win_counts.get(winner, 0) + 1

    drivers = list(win_counts.keys())
    wins = list(win_counts.values())

    plt.bar(drivers, wins)
    plt.xlabel('Drivers')
    plt.ylabel('Number of Wins')
    plt.title('Number of Wins per Driver in Grand Prix')
    plt.xticks(rotation=90)

    plt.savefig(image_path)
    plt.close()