import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import plotly.graph_objects as go
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Spotify Intelligence Dashboard",
    page_icon="🎵",
    layout="wide",
)

# --- AUTHENTICATION (THE FINAL, CORRECTED METHOD) ---
# This version uses the powerful OAuth login but with a general scope
# which will solve the 403 Forbidden error for public data like audio-features.
def get_spotipy_client():
    auth_manager = SpotifyOAuth(
        client_id=st.secrets["SPOTIPY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
        scope=None,  # THE CRITICAL FIX: We request a general token, not a specific permission.
        cache_path=".spotipyoauthcache"
    )
    # This is a necessary step to get the token after the user logs in
    try:
        token_info = auth_manager.get_cached_token()
        if not token_info:
            # If no token, the user will be redirected to log in.
            # We can't proceed here, Streamlit will handle the redirect.
            st.stop()
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        st.error("Authentication process failed.")
        st.exception(e)
        st.stop()


try:
    sp = get_spotipy_client()
except Exception as e:
    st.error("Could not initialize Spotify client.")
    st.stop()

# --- TOP NAVBAR ---
st.title("🎵 Spotify Intelligence Dashboard")
if 'page' not in st.session_state:
    st.session_state.page = "Audio DNA Visualizer"

with st.container():
    cols = st.columns(3)
    with cols[0]:
        if st.button("🎧 Audio DNA Visualizer", use_container_width=True):
            st.session_state.page = "Audio DNA Visualizer"
    with cols[1]:
        if st.button("⌛ Musical Time Machine", use_container_width=True):
            st.session_state.page = "Musical Time Machine"
    with cols[2]:
        if st.button("🗺️ Infinite Genre Explorer", use_container_width=True):
            st.session_state.page = "Infinite Genre Explorer"
st.markdown("---")


# --- PAGE 1: AUDIO DNA VISUALIZER ---
if st.session_state.page == "Audio DNA Visualizer":
    st.header("🎧 Audio DNA Visualizer")
    st.write("Search for any song to see its unique 'audio fingerprint' and listen to a preview.")

    song_query = st.text_input("Search for a song title", "")
    
    if song_query:
        try:
            # Search for the track
            results = sp.search(q=f"track:{song_query}", type='track', limit=1)
            
            if not results['tracks']['items']:
                st.warning("No song found with that name. Please try another.")
            else:
                track = results['tracks']['items'][0]
                track_id = track['id']
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                album_art_url = track['album']['images'][0]['url']
                preview_url = track['preview_url']

                st.subheader(f"{track_name} by {artist_name}")

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(album_art_url, use_column_width=True)
                    if preview_url:
                        st.audio(preview_url)
                    else:
                        st.warning("No audio preview available for this track.")

                # This API call will now succeed
                audio_features = sp.audio_features(track_id)[0]
                
                with col2:
                    st.markdown("#### Audio Fingerprint")
                    features_to_plot = {
                        'Danceability': audio_features['danceability'],
                        'Energy': audio_features['energy'],
                        'Valence (Happiness)': audio_features['valence'],
                        'Acousticness': audio_features['acousticness'],
                        'Speechiness': audio_features['speechiness'],
                        'Instrumentalness': audio_features['instrumentalness']
                    }
                    
                    df = pd.DataFrame(dict(r=list(features_to_plot.values()), theta=list(features_to_plot.keys())))
                    fig = go.Figure(data=go.Scatterpolar(r=df['r'], theta=df['theta'], fill='toself', marker=dict(color='#1DB954')))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1]), bgcolor='#2E2E2E'),
                        showlegend=False, paper_bgcolor="#121212", font_color="white", height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error("An error occurred. This can sometimes happen if Spotify's API is temporarily unavailable. Please try refreshing.")
            st.exception(e)

# --- PLACEHOLDER PAGES ---
elif st.session_state.page == "Musical Time Machine":
    st.header("⌛ Musical Time Machine")
    st.info("Coming soon!")
elif st.session_state.page == "Infinite Genre Explorer":
    st.header("🗺️ Infinite Genre Explorer")
    st.info("Coming soon!")