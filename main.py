import requests
import subprocess
import argparse
from dotenv import load_dotenv
import os
import re

load_dotenv()


def get_spotify_access_token():
    client_id = os.getenv("client_id")
    client_secret = os.getenv("client_secret")

    if not client_id or not client_secret:
        raise ValueError("Client ID and Client Secret must be set as environment variables.")

    # make the request
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")

# Spotify API endpoint for fetching playlist tracks
BASE_URL = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

def export_id(url):
    match = re.search(r"(?<=playlist\/)[\w\d]+", url)
    if match:
        return match.group(0)
    else:
        raise ValueError("the url is not correct")

# Replace with your token and playlist ID
ACCESS_TOKEN = get_spotify_access_token()
PLAYLIST_URL = input("enter your spotify link: ")
PLAYLIST_ID = export_id(PLAYLIST_URL)


def get_playlist_tracks(access_token, playlist_id):
    url = BASE_URL.format(playlist_id=playlist_id)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        tracks = []

        for item in data.get('items', []):
            track = item.get('track', {})
            track_details = {
                "track_name": track.get("name"),
                "artist_name": ", ".join(artist.get("name") for artist in track.get("artists", [])),
                "album_name": track.get("album", {}).get("name"),
                "length_ms": track.get("duration_ms"),
                "cover_url": track.get("album", {}).get("images", [{}])[0].get("url"),
                "track_url": track.get("external_urls", {}).get("spotify")
            }
            tracks.append(track_details)

        return tracks
    else:
        print(f"Failed to fetch playlist tracks: {response.status_code} - {response.text}")
        return []


def send_tg():
  tmp = list(os.scandir('.'))
  bot_token = os.getenv("bot_token")
  chat_id = os.getenv("chat_id")
  for i in tmp:
    if 'mp3' in i.name:
        file ={"document": open(f'{i.name}', 'rb')}
        res = requests.post(f"https://api.telegram.org/bot{bot_token}/sendDocument?chat_id={chat_id}", files=file)
        print(res.content)


# Call the function and display the results
if __name__ == "__main__":
    tracks = get_playlist_tracks(ACCESS_TOKEN, PLAYLIST_ID)

    if tracks:
        print("Tracks in the Playlist:")
        for idx, track in enumerate(tracks, 1):
            print(f"{idx}. {track['track_name']} by {track['artist_name']}")
            print(f"   Album: {track['album_name']}")
            print(f"   Length: {track['length_ms']} ms")
            print(f"   Cover URL: {track['cover_url']}")
            print(f"   Track URL: {track['track_url']}")
            print()
            subprocess.run(['spotdl', track['track_url']])   
        print("Downloading tracks ended, now uploading on telegram")
        send_tg() 



