import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Optional, Dict
import time

class DynamicJuiceWRLDPlaylistCreator:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize Spotify client with OAuth authentication
        """
        self.scope = "playlist-modify-public playlist-modify-private"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=self.scope
        ))
    
    def get_artist_id(self, artist_name: str = "Juice WRLD") -> Optional[str]:
        """Get the Spotify artist ID for Juice WRLD"""
        try:
            results = self.sp.search(q=f"artist:{artist_name}", type='artist', limit=1)
            if results['artists']['items']:
                return results['artists']['items'][0]['id']
            return None
        except Exception as e:
            print(f"Error getting artist ID: {e}")
            return None
    
    def get_all_albums(self, artist_id: str) -> List[Dict]:
        """Get all albums for an artist"""
        albums = []
        try:
            # Get albums, singles, and appears_on
            for album_type in ['album', 'single', 'appears_on']:
                results = self.sp.artist_albums(
                    artist_id, 
                    album_type=album_type, 
                    limit=50,
                    country='US'
                )
                albums.extend(results['items'])
                
                # Handle pagination
                while results['next']:
                    results = self.sp.next(results)
                    albums.extend(results['items'])
            
            return albums
        except Exception as e:
            print(f"Error getting albums: {e}")
            return []
    
    def get_tracks_from_albums(self, albums: List[Dict]) -> List[Dict]:
        """Extract all tracks from albums"""
        all_tracks = []
        seen_tracks = set()  # To avoid duplicates
        
        for album in albums:
            try:
                # Get tracks from this album
                tracks = self.sp.album_tracks(album['id'])
                
                for track in tracks['items']:
                    # Check if Juice WRLD is the main artist or featured
                    juice_wrld_track = any(
                        'juice' in artist['name'].lower() and 'wrld' in artist['name'].lower() 
                        for artist in track['artists']
                    )
                    
                    if juice_wrld_track:
                        track_key = f"{track['name'].lower()}_{track['artists'][0]['name'].lower()}"
                        if track_key not in seen_tracks:
                            track_info = {
                                'name': track['name'],
                                'uri': track['uri'],
                                'artists': [artist['name'] for artist in track['artists']],
                                'album': album['name'],
                                'release_date': album.get('release_date', ''),
                                'popularity': 0,  # Will be filled later
                                'audio_features': {}  # Will be filled later
                            }
                            all_tracks.append(track_info)
                            seen_tracks.add(track_key)
                
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing album {album['name']}: {e}")
                continue
        
        return all_tracks
    
    def get_track_details(self, tracks: List[Dict]) -> List[Dict]:
        """Get detailed information for tracks including audio features"""
        print("🔍 Getting detailed track information...")
        
        # Get track details in batches of 50 (Spotify API limit)
        for i in range(0, len(tracks), 50):
            batch = tracks[i:i+50]
            track_ids = [track['uri'].split(':')[-1] for track in batch]
            
            try:
                # Get track details (including popularity)
                track_details = self.sp.tracks(track_ids)
                
                # Get audio features
                audio_features = self.sp.audio_features(track_ids)
                
                # Update tracks with detailed info
                for j, track in enumerate(batch):
                    if j < len(track_details['tracks']) and track_details['tracks'][j]:
                        track['popularity'] = track_details['tracks'][j]['popularity']
                    
                    if j < len(audio_features) and audio_features[j]:
                        track['audio_features'] = audio_features[j]
                
                print(f"📊 Processed batch {i//50 + 1}/{(len(tracks)-1)//50 + 1}")
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"Error getting track details for batch: {e}")
        
        return tracks
    
    def filter_slow_somber_tracks(self, tracks: List[Dict], limit: int = 100) -> List[Dict]:
        """Filter tracks based on audio features to find slow and somber ones"""
        print("🎭 Filtering for slow and somber tracks...")
        
        slow_somber_tracks = []
        
        for track in tracks:
            features = track.get('audio_features', {})
            if not features:
                continue
            
            # Criteria for slow and somber tracks
            valence = features.get('valence', 0.5)  # Lower = more negative/sad
            energy = features.get('energy', 0.5)    # Lower = less energetic
            tempo = features.get('tempo', 120)      # Lower = slower
            danceability = features.get('danceability', 0.5)  # Lower = less danceable
            
            # Define thresholds for "slow and somber"
            is_slow = tempo < 140  # BPM threshold
            is_somber = valence < 0.6  # Emotional threshold
            is_low_energy = energy < 0.7  # Energy threshold
            is_less_danceable = danceability < 0.7  # Danceability threshold
            
            # Calculate a "somber score"
            somber_score = (
                (1 - valence) * 0.4 +      # 40% weight on sadness
                (1 - energy) * 0.3 +       # 30% weight on low energy
                (140 - min(tempo, 140)) / 140 * 0.2 +  # 20% weight on slowness
                (1 - danceability) * 0.1   # 10% weight on non-danceability
            )
            
            if is_slow and is_somber and somber_score > 0.3:
                track['somber_score'] = somber_score
                slow_somber_tracks.append(track)
        
        # Sort by somber score (highest first) and popularity
        slow_somber_tracks.sort(
            key=lambda x: (x.get('somber_score', 0) * 0.7 + x.get('popularity', 0) / 100 * 0.3), 
            reverse=True
        )
        
        return slow_somber_tracks[:limit]
    
    def search_additional_tracks(self, limit: int = 20) -> List[Dict]:
        """Search for additional sad/emotional Juice WRLD tracks using keywords"""
        print("🔍 Searching for additional emotional tracks...")
        
        # Keywords associated with sad/emotional songs
        sad_keywords = [
            "sad", "cry", "pain", "hurt", "broken", "empty", "alone", 
            "depression", "anxiety", "lost", "lonely", "tears", "goodbye",
            "miss", "love", "heartbreak", "sorry", "regret", "dark"
        ]
        
        found_tracks = []
        seen_uris = set()
        
        for keyword in sad_keywords[:10]:  # Limit searches to avoid rate limiting
            try:
                query = f"artist:\"Juice WRLD\" {keyword}"
                results = self.sp.search(q=query, type='track', limit=10)
                
                for track in results['tracks']['items']:
                    if track['uri'] not in seen_uris:
                        # Check if Juice WRLD is the main artist
                        juice_wrld_track = any(
                            'juice' in artist['name'].lower() and 'wrld' in artist['name'].lower() 
                            for artist in track['artists']
                        )
                        
                        if juice_wrld_track:
                            track_info = {
                                'name': track['name'],
                                'uri': track['uri'],
                                'artists': [artist['name'] for artist in track['artists']],
                                'album': track['album']['name'],
                                'popularity': track['popularity'],
                                'somber_score': 0.5  # Default score
                            }
                            found_tracks.append(track_info)
                            seen_uris.add(track['uri'])
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"Error searching with keyword '{keyword}': {e}")
        
        return found_tracks[:limit]
    
    def create_playlist(self, name: str, description: str, public: bool = True) -> str:
        """Create a new Spotify playlist"""
        user_id = self.sp.me()['id']
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=name,
            public=public,
            description=description
        )
        return playlist['id']
    
    def add_tracks_to_playlist(self, playlist_id: str, tracks: List[Dict]):
        """Add tracks to playlist"""
        track_uris = [track['uri'] for track in tracks]
        
        # Add tracks in batches of 100
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i+100]
            self.sp.playlist_add_items(playlist_id, batch)
            print(f"✅ Added batch {i//100 + 1}: {len(batch)} tracks")
    
    def create_dynamic_juice_wrld_playlist(self, target_count: int = 100):
        """
        Dynamically create a Juice WRLD playlist by discovering tracks
        """
        print("🎵 Creating Dynamic Juice WRLD Slow & Somber Playlist...")
        print("🔍 This will automatically discover tracks based on audio analysis")
        print("=" * 60)
        
        # Step 1: Get Juice WRLD's artist ID
        print("1️⃣ Finding Juice WRLD on Spotify...")
        artist_id = self.get_artist_id()
        if not artist_id:
            print("❌ Could not find Juice WRLD on Spotify")
            return None
        print("✅ Found Juice WRLD!")
        
        # Step 2: Get all albums
        print("\n2️⃣ Getting all albums and releases...")
        albums = self.get_all_albums(artist_id)
        print(f"✅ Found {len(albums)} releases")
        
        # Step 3: Extract all tracks
        print("\n3️⃣ Extracting tracks from albums...")
        all_tracks = self.get_tracks_from_albums(albums)
        print(f"✅ Found {len(all_tracks)} total tracks")
        
        # Step 4: Get detailed track information
        print("\n4️⃣ Analyzing track characteristics...")
        detailed_tracks = self.get_track_details(all_tracks)
        
        # Step 5: Filter for slow and somber tracks
        print("\n5️⃣ Filtering for slow and somber vibes...")
        slow_somber_tracks = self.filter_slow_somber_tracks(detailed_tracks, target_count - 20)
        print(f"✅ Found {len(slow_somber_tracks)} slow & somber tracks from albums")
        
        # Step 6: Search for additional tracks if needed
        if len(slow_somber_tracks) < target_count:
            print(f"\n6️⃣ Searching for additional tracks to reach {target_count}...")
            additional_tracks = self.search_additional_tracks(target_count - len(slow_somber_tracks))
            slow_somber_tracks.extend(additional_tracks)
            print(f"✅ Added {len(additional_tracks)} additional tracks")
        
        # Step 7: Create playlist
        final_tracks = slow_somber_tracks[:target_count]
        print(f"\n7️⃣ Creating playlist with {len(final_tracks)} tracks...")
        
        playlist_name = "Dynamic Slow & Somber Juice WRLD 🖤"
        description = f"Automatically curated collection of {len(final_tracks)} slow and somber Juice WRLD tracks. Discovered using audio analysis and emotional keywords. 999 forever 🕊️"
        
        playlist_id = self.create_playlist(playlist_name, description)
        print(f"✅ Created playlist: {playlist_name}")
        
        # Step 8: Add tracks
        print(f"\n8️⃣ Adding tracks to playlist...")
        self.add_tracks_to_playlist(playlist_id, final_tracks)
        
        # Display results
        print(f"\n🎶 Successfully created playlist with {len(final_tracks)} tracks!")
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        print(f"🔗 Playlist URL: {playlist_url}")
        
        # Show some track info
        print(f"\n📝 Sample tracks added:")
        for i, track in enumerate(final_tracks[:10]):
            score = track.get('somber_score', 0)
            print(f"  {i+1:2d}. {track['name']} (Somber Score: {score:.2f})")
        
        if len(final_tracks) > 10:
            print(f"  ... and {len(final_tracks) - 10} more tracks")
        
        return playlist_id


def main():
    """Main function to run the dynamic playlist creator"""
    print("🎤 Dynamic Juice WRLD Spotify Playlist Creator")
    print("=" * 50)
    
    # Your Spotify app credentials
    CLIENT_ID = '43ad7527da4d47ea88d75fc04a9e5699'
    CLIENT_SECRET = 'f393f39f40a540d3ac231165e730aa10'
    REDIRECT_URI = 'http://127.0.0.1:8000/callback'
    
    try:
        # Create playlist creator instance
        creator = DynamicJuiceWRLDPlaylistCreator(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        
        # Ask user for playlist size
        try:
            target_count = int(input("How many tracks do you want in the playlist? (default: 100): ") or "100")
        except ValueError:
            target_count = 100
        
        # Create the playlist dynamically
        creator.create_dynamic_juice_wrld_playlist(target_count)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have:")
        print("1. Valid Spotify credentials")
        print("2. Spotify Premium account (for playlist creation)")
        print("3. Internet connection")


if __name__ == "__main__":
    # Install required package first:
    # pip install spotipy
    main()