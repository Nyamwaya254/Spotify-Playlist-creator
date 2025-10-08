# Spotify-Playlist-creator
Tired of manually creating playlists of your favorite artist? This Python script automates Spotify playlist creation  and management, saving you time while discovering new music.

# Features

🎵 Automatically searches for your Artists tracks in spotify in their albums,singles and where they are featured on.
📝 Creates a curated playlist with custom name and description
✅ Provides detailed feedback on found/not found tracks
🔗 Returns a direct link to the created playlist
📊 Handles batch processing for efficient playlist creation

# Prerequisites
 
python Dependancies
   '''python
   pip install spotipy

# Spotify Developer Account
You need to create a Spotify app to get API credentials:

Go to Spotify Developer Dashboard(https://developer.spotify.com/dashboard)
Log in with your Spotify account
Click "Create an App"
Fill in the app details:

App name: "Dave Playlist Creator" (or any name)
App description: "Creates playlists automatically"
Redirect URI: http://127.0.0.1:8000/callback


Note down your Client ID and Client Secret

# Update Credentials
The current code contains example credentials. You MUST replace them with your own: