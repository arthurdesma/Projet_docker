
# Racing Database Application

## Overview
This application is a FastAPI-based web service that integrates with MongoDB and Elasticsearch to provide a platform for managing and querying racing data, specifically Formula 1 race results and driver standings.

## Features
- Web interface to update and query racing data
- Data scraping from Formula 1 website
- MongoDB for data storage
- Elasticsearch for advanced search capabilities

## Requirements
- Docker and Docker Compose
- Python 3.8+
- FastAPI
- Elasticsearch
- MongoDB

## Installation
1. Clone the repository
2. Ensure Docker and Docker Compose are installed
3. Navigate to the project directory

## Usage
1. Start the application:
   ```bash
   docker-compose up -d --build
   ```
2. Access the web interface at `http://localhost:8000`
3. Using the Application:
   - Update Database: Use the provided forms on the website to update the database with new data.
   - Query Data: To retrieve real-time information, use the forms to query the database, specifying the desired year. After entering your query, click on the **Load or Search** button to make the data appear on the page.

*Note:* The application fetches real-time data on demand and does not store this data internally.

## Components
### FastAPI Application
- `main.py`: FastAPI application setup and endpoints

### Elasticsearch
- `elastic_search_folder`: Contains Elasticsearch integration for indexing and querying data

### MongoDB
- `mongoDB_folder`: MongoDB connection and data manipulation functions

### Data Scraping
- `scraping_folder`: Functions to scrape racing data from the Formula 1 website

### Static Files
- `statics`: JavaScript functions for client-side form handling and data display

### Templates
- `home.html`: Jinja2 template for the home page

## Docker Configuration
- `Dockerfile`: Docker configuration for the FastAPI application
- `docker-compose.yml`: Compose file to orchestrate the FastAPI app, MongoDB, and Elasticsearch services

## Endpoints
- `/`: Home page with options to update the database and query data
- `/update_database/`: Endpoint to trigger database update
- `/update_and_index/`: Endpoint to update the database and index data in Elasticsearch
- `/index_data/`: Endpoint for indexing data into Elasticsearch
- `/list_indices/`: Endpoint to list all indices in Elasticsearch
- `/search/driver_standings/`: Search endpoint for driver standings
- `/search/grand_prix_results/`: Search endpoint for Grand Prix results

## Contributing
Feel free to fork the project, create a new branch for your feature or bug fix, and submit a pull request. All contributions are welcome!
