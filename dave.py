import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Optional

class DavePlaylistCreator:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.scope = "playlist-modify-public playlist-modify-private"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id='43ad7527da4d47ea88d75fc04a9e5699',
            client_secret='f393f39f40a540d3ac231165e730aa10',
            redirect_uri='http://127.0.0.1:8000/callback',
            scope=self.scope
        ))

    def search_track(self, track_name: str, artist: str = "Dave") -> Optional[str]:
        try:
            query = f"track:{track_name} artist:{artist}"
            results = self.sp.search(q=query, type='track', limit=1)

            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                track_title = results['tracks']['items'][0]['name']
                print(f"✓ Found: {track_title}")
                return track_uri
            else:
                print(f"✗ Not found: {track_name}")
                return None
        except Exception as e:
            print(f"Error searching for {track_name}: {e}")
            return None

    def create_playlist(self, name: str, description: str, public: bool = True) -> str:
        user_id = self.sp.me()['id']
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=name,
            public=public,
            description=description
        )
        return playlist['id']

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]):
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i+100]
            self.sp.playlist_add_items(playlist_id, batch)
            print(f"Added batch {i//100 + 1}: {len(batch)} tracks")

    def create_dave_playlist(self):
        track_names = [
            "Lesley", "Heart Attack", "Both Sides of a Smile", "We're All Alone",
            "In the Fire", "Survivor’s Guilt", "Psycho", "Twenty to One", "Law of Attraction",
            "Environment", "Drama", "Location", "Verdansk", "My 24th Birthday", "Streatham",
            "Black", "Thiago Silva", "Question Time", "No Words", "Screwface Capital",
            "Professor X", "God’s Eye", "Hangman", "Picture Me", "Paper Cuts", "Purple Heart",
            "My 19th Birthday", "Wanna Know", "Disaster", "System", "Both Sides of a Smile",
            "In the Fire", "We're All Alone in This Together", "Reminds Me of You",
            "In the Fire", "Survivor's Guilt", "Three Rivers", "Stranger", "Tequila",
            "How I Met My Ex", "Calling Me Out", "Attitude", "Dave’s Joint", "100M’s",
            "Samantha", "JKYL+HYD", "Game Over", "Titanium", "God's Eye", "No Words",
            "End Credits", "Panic Attack", "Only You Freestyle", "East London", "Hoodies All Summer",
            "Wanna Know (Remix)", "Love Me", "Bronze", "True Say", "Westside", "100M’s",
            "All Alone", "Love Is Blind", "My 25th Birthday", "Back in My Bag", "Question Time",
            "Please", "Split Decision", "Revenge", "Let Me Live", "Back to Basics", "Progression",
            "Verdansk (Live)", "Clash", "Something to Prove", "Half Time", "Flex", "No Words (feat. MoStack)",
            "Psycho", "Picture Me", "Titanium", "Starlight", "Hangman", "In the Fire",
            "Both Sides of a Smile", "Lesley", "We're All Alone", "Survivor’s Guilt",
            "Three Rivers", "In the Fire", "Heart Attack", "Tequila", "We're All Alone in This Together",
            "End Credits", "Reminds Me of You", "My 24th Birthday", "Black (Live at the BRITs)", "Twenty to One",
            "Lesley (feat. Ruelle)", "God’s Eye", "Back in My Bag"
        ]

        print("🎵 Creating 100 Sombre & Melancholic Dave Playlist...")
        print(f"Searching for {len(track_names)} tracks...\n")

        found_tracks = []
        not_found = []

        for track in track_names:
            uri = self.search_track(track)
            if uri:
                found_tracks.append(uri)
            else:
                not_found.append(track)

        print(f"\n📊 Results:")
        print(f"Found: {len(found_tracks)} tracks")
        print(f"Not found: {len(not_found)} tracks")

        if not_found:
            print("\n❌ Not Found:")
            for t in not_found:
                print(f"  - {t}")

        if found_tracks:
            playlist_name = "100 Sombre & Melancholic Dave Songs 🕊️"
            description = "A collection of Dave's most reflective, moody, and emotional tracks. Deep lyricism and sombre storytelling at its best."

            playlist_id = self.create_playlist(playlist_name, description)
            print(f"\n✅ Created playlist: {playlist_name}")
            self.add_tracks_to_playlist(playlist_id, found_tracks)

            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            print(f"\n🔗 Playlist URL: {playlist_url}")
            return playlist_id
        else:
            print("❌ No tracks found.")
            return None

def main():
    print("🎧 Dave - Sombre Spotify Playlist Creator")
    print("=" * 40)

    CLIENT_ID = '43ad7527da4d47ea88d75fc04a9e5699'
    CLIENT_SECRET = 'f393f39f40a540d3ac231165e730aa10'
    REDIRECT_URI = 'http://127.0.0.1:8000/callback'

    try:
        creator = DavePlaylistCreator(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        creator.create_dave_playlist()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure:")
        print("1. Your Spotify credentials are valid")
        print("2. You are logged into Spotify")
        print("3. You have an internet connection")

if __name__ == "__main__":
    main()
