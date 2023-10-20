import requests
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime, timedelta

# Azure Storage configurations
connection_string = "your-azure-connection-string-here"
container_name = 'your-azure-container-here'
blob_name = 'lolmatches.json'

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# Create a set to keep track of unique matchIds
unique_match_ids = set()

# Function to upload logo to Azure and return the URL
def upload_logo_to_azure(team_id, logo_binary):
    logo_blob_name = f"{team_id}.png"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=logo_blob_name)
    blob_client.upload_blob(logo_binary, blob_type="BlockBlob", overwrite=True)
    return blob_client.url

# Create or load the logo cache JSON file
logo_cache_file_path = "logo_cache.json"
try:
    with open(logo_cache_file_path, "r") as cache_file:
        logo_cache = json.load(cache_file)
except FileNotFoundError:
    logo_cache = {}

# This list will accumulate the IDs of teams for which cached logos were used
cached_team_ids = []

def get_team_logo_cached(team_id, headers):
    team_id_str = str(team_id)
    if team_id_str in logo_cache:
        # Accumulate the team_id instead of printing it
        cached_team_ids.append(team_id)
        return logo_cache[team_id_str]
    else:
        print(f"Caching logo for team {team_id}")
        logo_url = f"https://allsportsapi2.p.rapidapi.com/api/esport/team/{team_id}/image"
        logo_response = requests.get(logo_url, headers=headers)
        if logo_response.status_code == 200:
            content_type = logo_response.headers.get('Content-Type', '')
            if 'image' in content_type:
                azure_url = upload_logo_to_azure(team_id, logo_response.content)
                logo_cache[team_id_str] = azure_url
            else:
                logo_cache[team_id_str] = 'Logo not available due to unhandled content type'
        else:
            logo_cache[team_id_str] = 'Logo not available due to non-200 status code'
        with open(logo_cache_file_path, "w") as cache_file:
            json.dump(logo_cache, cache_file, indent=4)

# Fetch match data
today = datetime.now().strftime('%d/%m/%Y')
next_day = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
formatted_matches = []

for date in [today, next_day]:
    url = f"https://allsportsapi2.p.rapidapi.com/api/esport/matches/{date}"
    headers = {
        "X-RapidAPI-Key": "your_allsports_api_key", # get it free from here: https://rapidapi.com/fluis.lacasse/api/allsportsapi2
        "X-RapidAPI-Host": "allsportsapi2.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding the JSON response.")
            data = {}
        events = data.get('events', [])
        if events:
            for event in events:
                match_id = event.get('id')
                if match_id not in unique_match_ids:
                    unique_match_ids.add(match_id)
                    raw_timestamp = event.get('startTimestamp')
                    event_date = datetime.utcfromtimestamp(raw_timestamp).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    if event.get('tournament', {}).get('category', {}).get('flag') == 'lol':
                        team1_id = event.get('homeTeam', {}).get('id')
                        team2_id = event.get('awayTeam', {}).get('id')
                        team1_logo = get_team_logo_cached(team1_id, headers)
                        team2_logo = get_team_logo_cached(team2_id, headers)
                        formatted_match = {
                            'matchId': match_id,
                            'date': event_date,
                            'team1': event.get('homeTeam', {}).get('name', 'Team1 not specified'),
                            'team1Logo': team1_logo,
                            'team2': event.get('awayTeam', {}).get('name', 'Team2 not specified'),
                            'team2Logo': team2_logo,
                            'hoursUntilMatch': 'N/A',
                            'event': event.get('tournament', {}).get('name', ''),
                            'matchLink': f"https://some-link.com/match/{match_id}"
                        }
                        formatted_matches.append(formatted_match)
    else:
        print(f"Failed to get data: {response.content}")

with open("lolmatches.json", "w") as f:
    json.dump(formatted_matches, f, indent=4)

with open("lolmatches.json", "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
    print("\U0001F916Successfully uploaded lolmatches.json to Azure Blob Storage.")

# This line will print the summary at the end
print(f"Used cached LoL logos for team IDs: {', '.join(map(str, cached_team_ids))}")
