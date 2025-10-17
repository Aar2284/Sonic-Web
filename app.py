# app.py
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import json

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

@app.route('/api/generate-network', methods=['POST'])
def generate_network():
    if not sp:
        return jsonify({"error": "Spotify service is not available."}), 500

    artist_name = request.json.get('artist_name')
    if not artist_name:
        return jsonify({"error": "Artist name is required."}), 400

    try:
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
        if not results['artists']['items']:
            return jsonify({"error": f"Artist '{artist_name}' not found."}), 404
        
        main_artist = results['artists']['items'][0]
        main_artist_id = main_artist['id']
        main_artist_name = main_artist['name']

        # --- Prepare data for the frontend ---
        nodes = []
        edges = []
        node_data_for_flashcard = {}

        # Add main artist node
        main_artist_image = main_artist['images'][0]['url'] if main_artist['images'] else None
        nodes.append({'id': main_artist_name, 'shape': 'image', 'image': main_artist_image, 'size': 30, 'borderWidth': 4, 'color': {'border': '#1DB954'}})

        # Deep scan for collaborators
        collaborations = {}
        offset = 0
        limit = 50
        while len(collaborations) < 50:
            albums_response = sp.artist_albums(main_artist_id, album_type='album,single', limit=limit, offset=offset)
            if not albums_response['items']: break
            for album in albums_response['items']:
                tracks = sp.album_tracks(album['id'])['items']
                for track in tracks:
                    if len(track['artists']) > 1:
                        for artist in track['artists']:
                            if artist['name'] != main_artist_name:
                                collaborator_name = artist['name']
                                if collaborator_name not in collaborations: collaborations[collaborator_name] = []
                                track_image = album['images'][0]['url'] if album['images'] else ''
                                collaborations[collaborator_name].append({ "name": track['name'], "image": track_image })
                                if len(collaborations) >= 50: break
                if len(collaborations) >= 50: break
            offset += limit
        
        # Process collaborators
        for collaborator_name, tracks in collaborations.items():
            collab_image_url = ''
            try:
                collab_results = sp.search(q=f'artist:{collaborator_name}', type='artist', limit=1)
                if collab_results['artists']['items'] and collab_results['artists']['items'][0]['images']:
                    collab_image_url = collab_results['artists']['items'][0]['images'][0]['url']
            except Exception: pass
            
            nodes.append({'id': collaborator_name, 'shape': 'image' if collab_image_url else 'dot', 'image': collab_image_url, 'size': 20, 'color': '#1DB954' if not collab_image_url else None})
            edges.append({'from': main_artist_name, 'to': collaborator_name, 'color': '#cccccc'})
            
            # THE FIX IS HERE: We have removed the sorted() function
            node_data_for_flashcard[collaborator_name] = {"name": collaborator_name, "image": collab_image_url, "tracks": tracks}

        # Return pure JSON data for the frontend to render
        return jsonify({
            "success": True,
            "graph_data": {
                "nodes": nodes,
                "edges": edges
            },
            "flashcard_data": node_data_for_flashcard
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
