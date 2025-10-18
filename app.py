# app.py
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
app = Flask(__name__)

try:
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    print("Spotify authentication successful.")
except Exception as e:
    sp = None

@app.route('/')
def index():
    return render_template('index.html')

# NEW: Endpoint just for searching artists
@app.route('/api/generate-network', methods=['POST'])
def generate_network():
    if not sp:
        return jsonify({"error": "Spotify service is not available."}), 500

    artist_id = request.json.get('artist_id')
    if not artist_id:
        return jsonify({"error": "Artist ID is required."}), 400

    try:
        main_artist = sp.artist(artist_id)
        main_artist_name = main_artist['name']
        
        nodes, edges, node_data_for_flashcard = [], [], {}
        main_artist_image = main_artist['images'][0]['url'] if main_artist['images'] else None
        nodes.append({'id': main_artist_name, 'shape': 'image', 'image': main_artist_image, 'size': 30, 'borderWidth': 4, 'color': {'border': '#1DB954'}})

        collaborations, all_tracks_for_charts = {}, []
        offset, limit = 0, 50
        pages_fetched = 0
        page_limit = 4 # Limit scan depth

        print("Starting deep scan of discography...")
        while pages_fetched < page_limit:
            albums_response = sp.artist_albums(artist_id, album_type='album,single', limit=limit, offset=offset)
            if not albums_response['items']: break
            
            for album in albums_response['items']:
                if album['release_date'] and len(album['release_date']) >= 4:
                    tracks = sp.album_tracks(album['id'])['items']
                    for track in tracks:
                        all_tracks_for_charts.append({'id': track['id'], 'year': int(album['release_date'][:4]), 'popularity': track.get('popularity', 0)})
                        if len(collaborations) < 50 and len(track['artists']) > 1:
                            for artist in track['artists']:
                                if artist['name'] != main_artist_name:
                                    collaborator_name = artist['name']
                                    if collaborator_name not in collaborations: collaborations[collaborator_name] = []
                                    track_image = album['images'][0]['url'] if album['images'] else ''
                                    collaborations[collaborator_name].append({ "name": track['name'], "image": track_image })
            offset += limit
            pages_fetched += 1

        for collaborator_name, tracks in collaborations.items():
            collab_image_url = ''
            try:
                collab_results = sp.search(q=f'artist:{collaborator_name}', type='artist', limit=1)
                if collab_results['artists']['items'] and collab_results['artists']['items'][0]['images']:
                    collab_image_url = collab_results['artists']['items'][0]['images'][0]['url']
            except Exception: pass
            
            nodes.append({'id': collaborator_name, 'shape': 'image' if collab_image_url else 'dot', 'image': collab_image_url, 'size': 20, 'color': '#1DB954' if not collab_image_url else None})
            edges.append({'from': main_artist_name, 'to': collaborator_name, 'color': '#cccccc'})
            node_data_for_flashcard[collaborator_name] = {"name": collaborator_name, "image": collab_image_url, "tracks": tracks}

        # --- Part 2: Prepare chart data (WITH ISOLATED ERROR HANDLING) ---
        chart_data = None
        if all_tracks_for_charts:
            try:
                print("Processing tracks for career charts...")
                df = pd.DataFrame(all_tracks_for_charts)
                df.drop_duplicates(subset=['id'], inplace=True)
                
                # --- THIS IS THE MOST LIKELY POINT OF FAILURE ---
                print(f"Fetching audio features for {len(df['id'])} unique tracks...")
                audio_features = []
                # Fetch features in batches to be safe
                for i in range(0, len(df['id']), 50): # Smaller batches (50)
                    batch_ids = [tid for tid in df['id'][i:i+50].tolist() if tid] # Ensure IDs are not None
                    if not batch_ids: continue
                    try:
                        batch_features = sp.audio_features(batch_ids)
                        audio_features.extend([f for f in batch_features if f]) # Filter out None results
                    except Exception as batch_error:
                        print(f"WARNING: Failed to fetch audio features batch. Error: {batch_error}")
                        # Continue with the next batch even if one fails
                
                print(f"Successfully fetched features for {len(audio_features)} tracks.")
                if audio_features: # Proceed only if we got some features
                    features_df = pd.DataFrame(audio_features)
                    df = pd.merge(df, features_df, on='id', how='inner') # Use inner merge
                    if not df.empty and 'year' in df.columns:
                       yearly_stats = df.groupby('year').agg({
                           'popularity': 'mean',
                           'danceability': 'mean',
                           'energy': 'mean',
                           'valence': 'mean'
                       }).reset_index()
                       chart_data = yearly_stats.to_dict('records')
                       print("Chart data successfully generated.")
                    else:
                      print("WARNING: DataFrame empty after merge or 'year' column missing.")
                else:
                    print("WARNING: No valid audio features were retrieved.")
                    
            except Exception as e:
                # If ANY part of chart data fails, print a warning but keep going
                print(f"WARNING: Could not generate career charts. Reason: {e}")
                chart_data = None # Ensure chart_data is None on failure

        # --- Part 3: Return all available data ---
        print("Sending response to frontend.")
        return jsonify({
            "success": True,
            "graph_data": {"nodes": nodes, "edges": edges},
            "flashcard_data": node_data_for_flashcard,
            "chart_data": chart_data # Will be None if charts failed
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
