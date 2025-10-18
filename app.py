# app.py
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, render_template, request, jsonify
import networkx as nx
from pyvis.network import Network
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
    return render_template('artist_network.html')

# --- API Endpoint 1: Search for Artists ---
@app.route('/api/search-artist', methods=['POST'])
def search_artist():
    if not sp: return jsonify({"error": "Spotify service is not available."}), 500
    artist_name = request.json.get('artist_name')
    if not artist_name: return jsonify({"error": "Artist name is required."}), 400
    try:
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=5)
        artists = []
        for item in results['artists']['items']:
            artists.append({"id": item['id'], "name": item['name'], "image": item['images'][0]['url'] if item['images'] else None, "genres": item['genres'], "popularity": item['popularity']})
        print(f"Search for '{artist_name}' found {len(artists)} results.")
        return jsonify({"success": True, "artists": artists})
    except Exception as e:
        print(f"Error during artist search: {e}")
        return jsonify({"error": str(e)}), 500

# --- API Endpoint 2: Generate Network Graph ---
@app.route('/api/generate-network', methods=['POST'])
def generate_network():
    if not sp: return jsonify({"error": "Spotify service is not available."}), 500
    artist_id = request.json.get('artist_id')
    if not artist_id: return jsonify({"error": "Artist ID is required."}), 400

    try:
        main_artist = sp.artist(artist_id)
        main_artist_name = main_artist['name']
        main_artist_image = main_artist['images'][0]['url'] if main_artist['images'] else ''
        print(f"Generating network for: {main_artist_name} (ID: {artist_id})")

        G = nx.Graph()
        node_data_for_flashcard = {} # Store data for flashcards
        G.add_node(main_artist_name, size=30, title=main_artist_name, shape='image' if main_artist_image else 'dot', image=main_artist_image)

        # --- Collaborator Scan ---
        collaborations = {}
        all_tracks_for_charts = []
        offset, limit, pages_fetched, page_limit = 0, 50, 0, 4
        while pages_fetched < page_limit:
            albums_response = sp.artist_albums(artist_id, album_type='album,single', limit=limit, offset=offset)
            if not albums_response['items']: break
            for album in albums_response['items']:
                release_date = album.get('release_date')
                if release_date and len(release_date) >= 4:
                    try:
                        year = int(release_date[:4])
                        tracks = sp.album_tracks(album['id'])['items']
                        for track in tracks:
                            all_tracks_for_charts.append({'id': track['id'], 'year': year, 'popularity': track.get('popularity', 0)})
                            if len(collaborations) < 50 and len(track['artists']) > 1:
                                for artist in track['artists']:
                                    if artist['name'] != main_artist_name:
                                        collaborator_name = artist['name']
                                        if collaborator_name not in collaborations: collaborations[collaborator_name] = []
                                        track_image = album['images'][0]['url'] if album['images'] else ''
                                        # Store only name and image for tracks
                                        collaborations[collaborator_name].append({ "name": track['name'], "image": track_image })
                    except ValueError: continue
            offset += limit
            pages_fetched += 1
        print(f"Found {len(collaborations)} unique collaborators.")

        # --- Add Collaborator Nodes & Prepare Flashcard Data ---
        for collaborator_name, tracks in collaborations.items():
            collab_image_url = ''
            try:
                collab_results = sp.search(q=f'artist:{collaborator_name}', type='artist', limit=1)
                if collab_results['artists']['items'] and collab_results['artists']['items'][0]['images']:
                    collab_image_url = collab_results['artists']['items'][0]['images'][0]['url']
            except Exception: pass
            
            # Add node to graph (simple title)
            G.add_node(collaborator_name, size=20, title=collaborator_name, shape='image' if collab_image_url else 'dot', image=collab_image_url, color='#1DB954' if not collab_image_url else None)
            G.add_edge(main_artist_name, collaborator_name, color='#cccccc')
            
            # Store data for the flashcard (without popularity)
            node_data_for_flashcard[collaborator_name] = {"name": collaborator_name, "image": collab_image_url, "tracks": tracks}

        # --- Generate Chart Data ---
        chart_data = None
        # ... (Chart data generation logic remains unchanged) ...
        try:
             if all_tracks_for_charts:
                 df = pd.DataFrame(all_tracks_for_charts)
                 df.drop_duplicates(subset=['id'], inplace=True)
                 audio_features = []
                 for i in range(0, len(df['id']), 50):
                     batch_ids = [tid for tid in df['id'][i:i+50].tolist() if tid]
                     if not batch_ids: continue
                     try:
                         batch_features = sp.audio_features(batch_ids)
                         audio_features.extend([f for f in batch_features if f])
                     except Exception as batch_error: print(f"WARNING: Failed audio features batch. Error: {batch_error}")
                 if audio_features:
                     features_df = pd.DataFrame(audio_features)
                     if 'id' in df.columns and 'id' in features_df.columns:
                         df = pd.merge(df, features_df, on='id', how='inner')
                         if not df.empty and 'year' in df.columns:
                             yearly_stats = df.groupby('year').agg({'popularity': 'mean', 'danceability': 'mean', 'energy': 'mean', 'valence': 'mean'}).reset_index()
                             chart_data = yearly_stats.to_dict('records')
                             print("Chart data generated.")
                         else: print("WARNING: DataFrame empty or 'year' missing post-merge.")
                     else: print("WARNING: 'id' column missing for merge.")
                 else: print("WARNING: No valid audio features retrieved.")
        except Exception as e:
             print(f"WARNING: Chart generation failed. Reason: {e}")
             chart_data = None

        # --- Generate Graph HTML with Pyvis ---
        net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        net.from_nx(G)
        net.set_options("""
        {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -30000, "centralGravity": 0.1, "springLength": 150
            },
            "minVelocity": 0.75
          }
        }
        """)

        graph_filename = 'artist_network.html'
        graph_path = os.path.join('templates', graph_filename)
        net.save_graph(graph_path)

        # Read the HTML to inject click listener
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph_html = f.read()

        # Inject JS snippet to send click events to parent
        click_handler_js = """
        <script type="text/javascript">
            if (network) {
                network.on('click', function(params) {
                    if (params.nodes.length > 0) {
                        var clickedNodeId = params.nodes[0];
                        window.parent.postMessage({ type: 'node_clicked', nodeId: clickedNodeId }, '*');
                    }
                });
            }
        </script>
        """
        modified_html = graph_html.replace('</body>', click_handler_js + '</body>')

        # Return graph HTML and flashcard data
        return jsonify({
            "success": True,
            "graph_html": modified_html, # Send modified HTML for iframe
            "flashcard_data": node_data_for_flashcard, # Send data for JS popups
            "chart_data": chart_data,
            "artist_name": main_artist_name
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Route to serve the generated graph HTML (not strictly needed with srcdoc but good fallback)
# @app.route('/artist_network.html')
# def artist_network():
#    return render_template('artist_network.html')

if __name__ == '__main__':
    app.run(debug=True)
