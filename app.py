import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Musical Time Machine",
    page_icon="⌛",
    layout="wide",
)

# --- AUTHENTICATION (THE SIMPLE, WORKING METHOD) ---
# This method does not require user login and is perfect for public data.
# It will not cause any more 403 Forbidden errors.
def get_spotipy_client():
    auth_manager = SpotifyClientCredentials(
        client_id=st.secrets["SPOTIPY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
    )
    return spotipy.Spotify(auth_manager=auth_manager)

try:
    sp = get_spotipy_client()
except Exception as e:
    st.error("Authentication failed. Please check your Client ID and Secret in secrets.toml.")
    st.stop()


# --- APP UI ---
st.title("⌛ Musical Time Machine")
st.write("Enter any year to see the top hits from that time.")

# Get the current year
current_year = datetime.now().year

# Year selection
year = st.number_input(
    "Enter a year",
    min_value=1950,
    max_value=current_year,
    value=current_year - 1 # Default to last year
)

if st.button("Travel to Year!", use_container_width=True):
    try:
        with st.spinner(f"Searching for the top hits of {year}..."):
            # Use a smarter search query to get relevant songs
            query = f'year:{year}'
            results = sp.search(q=query, type='track', limit=10, offset=0)
            
            if not results['tracks']['items']:
                st.warning(f"Could not find any top tracks for the year {year}.")
            else:
                st.subheader(f"Top Hits from {year}")
                
                # Display results in columns for a clean look
                cols = st.columns(5)
                for i, track in enumerate(results['tracks']['items'][:5]):
                    with cols[i]:
                        if track['album']['images']:
                            st.image(track['album']['images'][0]['url'], use_column_width=True)
                        st.write(f"**{track['name']}**")
                        st.caption(track['artists'][0]['name'])
                        if track['preview_url']:
                            st.audio(track['preview_url'])

    except Exception as e:
        st.error("An error occurred while fetching data. Spotify's API might be temporarily down.")
        st.exception(e)
