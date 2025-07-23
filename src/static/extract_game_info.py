import os
import requests
from dotenv import load_dotenv
load_dotenv()

def get_igdb_game_info(game_name):
    """
    Fetch game info from IGDB API using the API key in the environment variable 'IGDB_API_KEY'.
    Returns the first matching game's info as a dict, or None if not found.
    """
    client_id = os.getenv('TWITCH_CLIENT_ID')
    api_key = os.getenv('IGDB_API_KEY')
    if not client_id or not api_key:
        raise EnvironmentError('TWITCH_CLIENT_ID and IGDB_API_KEY must be set in environment variables.')

    # Get OAuth token from Twitch
    auth_url = 'https://id.twitch.tv/oauth2/token'
    auth_data = {
        'client_id': client_id,
        'client_secret': api_key,
        'grant_type': 'client_credentials'
    }
    auth_resp = requests.post(auth_url, data=auth_data)
    auth_resp.raise_for_status()
    access_token = auth_resp.json()['access_token']

    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    url = 'https://api.igdb.com/v4/games'
    body = f'search "{game_name}"; fields name,summary,cover.url,genres.name,platforms.name; limit 1;'
    resp = requests.post(url, headers=headers, data=body)
    resp.raise_for_status()
    results = resp.json()
    if results:
        game_info = results[0]
        # Prepare JSON object
        game_json = {
            "name": game_info.get("name"),
            "summary": game_info.get("summary"),
            "genres": [g.get("name") for g in game_info.get("genres", [])] if game_info.get("genres") else [],
            "platforms": [p.get("name") for p in game_info.get("platforms", [])] if game_info.get("platforms") else [],
            "image": game_info.get("cover", {}).get("url"),
        }
        # Load existing list
        import json
        import os
        
        # Get the path relative to the script's current directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(script_dir, "game_info.json")
        
        try:
            with open(json_path, "r") as f:
                game_list = json.load(f)
        except Exception:
            game_list = []
        game_list.append(game_json)
        with open(json_path, "w") as f:
            json.dump(game_list, f, indent=2)
        print(f"Game info saved to {json_path}")
        return game_json
    else:
        print(f'No results found for {game_name}')
        return None

if __name__ == '__main__':
    get_igdb_game_info("Palworld")
