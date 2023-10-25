# LoL Match Data Fetcher 🦉

This Python application fetches upcoming match data for League of Legends from the free AllSportsAPI. It creates a JSON file (`lolmatches.json`) that contains information about matches scheduled for the next 48 hours. Additionally, it uploads the logos of the teams to Azure Blob Storage and includes the logo URLs in the generated JSON. The `lolmatches.json` file is also uploaded to Azure Blob Storage for easy access.

## Requirements

- Python 3.x
- `requests` library
- Azure Blob Storage account
- AllSportsAPI key (free)

## How it Works

### Data Collection

1. Fetches match data from the free AllSportsAPI.
2. Retrieves or caches team logos.
3. Compiles all match data into a single JSON file (`lolmatches.json`).

### Azure Blob Storage

The application uses Azure Blob Storage to upload team logos. These logos are stored in a specified blob container and their URLs are included in the `lolmatches.json` for easy access. The `lolmatches.json` is also uploaded to the blob container.

## Frontend

The frontend for this project is available as a separate Chrome extension that reads the generated and uploaded `lolmatches.json`. You can find it in the following repository: [LoL-Esports-Chrome-Extension](https://github.com/netistul/LoL-Esports-Chrome-Extension).

## Setup and Usage

1. Clone this repository.
2. Install required Python packages.
3. Add your Azure Blob Storage connection string and container name in the Python script.
4. Obtain a free AllSportsAPI key and add it to the Python script.
5. Run the Python script to generate and upload `lolmatches.json` to Azure Blob Storage.
