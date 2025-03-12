# 1) https://pypi.org/project/streamlit/

# 2) Terminal: cd Birds > pip install -r requirements.txt
#                       > streamlit run app.py

# 3) Welcome to Streamlit! / You can now view your Streamlit app in your browser
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

import streamlit as st
import requests
import time
import pyaudio
import wave
import numpy as np
import tempfile
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Bird Song Recognition",
    page_icon="🦜",
    layout="wide"
)

# Dictionary of regions and their country codes
REGIONS = {
    "Europe": {
        "Spain": "spain",
        "France": "france",
        "Portugal": "portugal",
        "Italy": "italy",
        "United Kingdom": "united kingdom",
        "Germany": "germany",
        "Netherlands": "netherlands",
        "Sweden": "sweden",
        "Norway": "norway",
        "Finland": "finland"
    },
    "North America": {
        "United States": "united states",
        "Canada": "canada"
    },
    "Central America": {
        "Mexico": "mexico",
        "Costa Rica": "costa rica",
        "Panama": "panama",
        "Guatemala": "guatemala",
        "Honduras": "honduras",
        "El Salvador": "el salvador",
        "Nicaragua": "nicaragua",
        "Belize": "belize"
    },
    "South America": {
        "Argentina": "argentina",
        "Brazil": "brazil",
        "Colombia": "colombia",
        "Chile": "chile",
        "Peru": "peru",
        "Ecuador": "ecuador",
        "Venezuela": "venezuela"
    },
    "Asia": {
        "Japan": "japan",
        "China": "china",
        "India": "india",
        "Thailand": "thailand",
        "Vietnam": "vietnam",
        "Malaysia": "malaysia",
        "Indonesia": "indonesia"
    },
    "Oceania": {
        "Australia": "australia",
        "New Zealand": "new zealand",
        "Papua New Guinea": "papua new guinea",
        "Fiji": "fiji"
    },
    "Africa": {
        "South Africa": "south africa",
        "Kenya": "kenya",
        "Tanzania": "tanzania",
        "Uganda": "uganda",
        "Madagascar": "madagascar",
        "Ethiopia": "ethiopia"
    }
}

# Recording quality
QUALITY_RATINGS = {
    "All": "",
    "Good or better (A/B)": "q:A,B",
    "Excellent (A)": "q:A",
    "Verified only": "q_gt:C"
}

# Song types
SONG_TYPES = {
    "All": "type:all",
    "Song": "type:song",
    "Call": "type:call",
    "Drumming": "type:drumming"
}

# Cache for species information
@st.cache_data(ttl=3600)
def get_species_info(scientific_name):
    """
    Get species information from Wikipedia
    Args:
        scientific_name: Scientific name of the species
    Returns:
        dict: Species information
    """
    try:
        # MediaWiki API
        api_url = "https://en.wikipedia.org/w/api.php"
        
        # First search for the correct title
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": scientific_name,
            "utf8": 1
        }
        
        response = requests.get(api_url, params=search_params, timeout=10)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data['query']['search']:
            # Try with the common name
            common_name = scientific_name.split('(')[-1].strip(')')
            search_params["srsearch"] = common_name
            response = requests.get(api_url, params=search_params, timeout=10)
            response.raise_for_status()
            search_data = response.json()
            
            if not search_data['query']['search']:
                return None
        
        # Get the first result
        page_title = search_data['query']['search'][0]['title']
        
        # Get the page content
        content_params = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "extracts|pageimages",
            "exintro": True,
            "explaintext": True,
            "pithumbsize": 300,
            "utf8": 1
        }
        
        response = requests.get(api_url, params=content_params, timeout=10)
        response.raise_for_status()
        content_data = response.json()
        
        # Process the response
        pages = content_data['query']['pages']
        page_id = next(iter(pages))
        page_info = pages[page_id]
        
        image_url = None
        if 'thumbnail' in page_info:
            image_url = page_info['thumbnail']['source']
            
        return {
            "title": page_info['title'],
            "summary": page_info['extract'],
            "url": f"https://en.wikipedia.org/wiki/{page_info['title'].replace(' ', '_')}",
            "image_url": image_url
        }
        
    except requests.RequestException as e:
        st.warning(f"Error getting Wikipedia information: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_ebird_info(scientific_name):
    """
    Get species information from eBird
    Args:
        scientific_name: Scientific name of the species
    Returns:
        dict: Species information from eBird
    """
    try:
        # Convert scientific name to search format
        search_name = scientific_name.replace(' ', '+')
        url = f"https://api.ebird.org/v2/ref/taxonomy/ebird?fmt=json&name={search_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]
    except requests.RequestException as e:
        st.warning(f"Could not get eBird information: {str(e)}")
    return None

# Custom CSS styles
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .bird-info {
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .species-image {
        max-width: 300px;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .species-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main title
st.title("🦜 Bird Song :blue[Recognition]")

# Recording settings
CHUNK = 8192  # Increased for better performance
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
MAX_DURATION = 60  # seconds

def record_audio(duration):
    """
    Record audio using the microphone in an optimized way
    Args:
        duration: Recording duration in seconds
    Returns:
        str: Path to the recorded temporary file
    """
    # Create temporary directory if it does not exist
    temp_dir = os.path.join(tempfile.gettempdir(), 'bird_recordings')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique name for the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = os.path.join(temp_dir, f'recording_{timestamp}.wav')
    
    p = pyaudio.PyAudio()
    
    try:
        # Configure stream with a larger buffer
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        total_chunks = int(RATE * duration / CHUNK)
        update_interval = max(1, total_chunks // 10)  # Update progress every 10%
        
        # Show progress bar
        progress_bar = st.progress(0)
        progress_text = st.empty()
        progress_text.text("⏺️ Preparing recording...")
        
        # Pre-allocate memory for the frames
        frames = []
        
        # Record audio with less frequent updates
        for chunk in range(total_chunks):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Update progress only every interval
            if chunk % update_interval == 0:
                progress = int((chunk + 1) / total_chunks * 100)
                progress_bar.progress(progress)
                progress_text.text(f"⏺️ Recording... {progress}%")
        
        progress_text.text("💾 Saving recording...")
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        
        # Save WAV file in an optimized way
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            # Join frames efficiently
            wf.writeframes(b''.join(frames))
        
        # Clean up UI
        progress_bar.empty()
        progress_text.empty()
        
        return temp_file
        
    finally:
        p.terminate()

def save_audio(recording, sample_rate):
    """
    Save the recorded audio to a temporary file
    Args:
        recording: Recorded audio
        sample_rate: Sample rate
    Returns:
        str: Path to the temporary file
    """
    # Create temporary directory if it does not exist
    temp_dir = os.path.join(tempfile.gettempdir(), 'bird_recordings')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique name for the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = os.path.join(temp_dir, f'recording_{timestamp}.wav')
    
    # Save file
    with wave.open(temp_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16 bits
        wf.setframerate(sample_rate)
        wf.writeframes(recording)
    return temp_file

def search_xeno_canto(query):
    """
    Search for recordings on Xeno-canto
    Args:
        query: Search terms
    Returns:
        dict: Search results
    """
    base_url = "https://xeno-canto.org/api/2/recordings"
    params = {
        "query": query
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Xeno-canto: {str(e)}")
        return None

def search_recordings(country_code, quality_filter, song_type):
    """
    Search for recordings based on the selected filters
    Args:
        country_code: Country code for the search
        quality_filter: Selected quality filter
        song_type: Selected song type
    Returns:
        dict: Search results
    """
    query_parts = []
    
    # Add country to the query
    if country_code:
        query_parts.append(f"cnt:{country_code}")
    
    # Add quality to the query
    if quality_filter:
        query_parts.append(quality_filter)
    
    # Add song type
    if song_type and song_type != "type:all":
        query_parts.append(song_type)
    
    # Join all query parts
    query = " ".join(query_parts)
    return search_xeno_canto(query)

# Function to get the country from coordinates
def get_country_from_coords(lat, lon):
    """
    Get the country and continent using reverse geocoding
    Args:
        lat: Latitude
        lon: Longitude
    Returns:
        tuple: (region, country) or (None, None) if not found
    """
    try:
        # Use Nominatim for reverse geocoding (free and no API key)
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {
            'User-Agent': 'BirdSongApp/1.0'
        }
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        
        if 'address' in data and 'country' in data['address']:
            country = data['address']['country'].lower()
            # Find the corresponding region
            for region, countries in REGIONS.items():
                if any(country in c.lower() for c in countries.values()):
                    return region, list(countries.keys())[list(map(str.lower, countries.values())).index(country)]
    except Exception as e:
        st.warning(f"Could not determine location: {str(e)}")
    
    return None, None

# Custom component for geolocation
def get_location():
    """
    Component to get the user's location
    Returns:
        dict: Coordinates {lat, lon} or None if not obtained
    """
    component = """
    <div id="geolocation">
        <script>
        if (!window.locationSent) {
            window.locationSent = true;
            
            const sendLocation = async () => {
                if (navigator.geolocation) {
                    try {
                        const position = await new Promise((resolve, reject) => {
                            navigator.geolocation.getCurrentPosition(resolve, reject, {
                                enableHighAccuracy: true,
                                timeout: 5000,
                                maximumAge: 0
                            });
                        });
                        
                        const coords = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        };
                        
                        window.Streamlit.setComponentValue(coords);
                    } catch (error) {
                        console.error('Error getting location:', error);
                        window.Streamlit.setComponentValue(null);
                    }
                } else {
                    console.error('Geolocation not supported');
                    window.Streamlit.setComponentValue(null);
                }
            };
            
            // Initialize when the component is ready
            window.Streamlit.setComponentReady();
            sendLocation();
        }
        </script>
    </div>
    """
    return st.components.v1.html(component, height=0)

# Sidebar with configuration and information
with st.sidebar:
    st.header(":blue[Search Configuration]")
    
    # Get location
    use_location = st.checkbox("📍 Use my location", value=True,
                             help="Automatically detect your location to search for birds in your region")
    
    if use_location:
        with st.spinner("Detecting location..."):
            location_data = get_location()
            if isinstance(location_data, dict) and 'lat' in location_data and 'lon' in location_data:
                region, country = get_country_from_coords(location_data['lat'], location_data['lon'])
                if region and country:
                    st.success(f"📍 Location detected: {country}")
                    selected_region = region
                    selected_country = country
                else:
                    st.warning("Could not determine your location. Please select manually.")
                    use_location = False
            else:
                st.warning("Could not access location. Please check your browser settings.")
                use_location = False
    
    if not use_location:
        # Manual region selection
        selected_region = st.selectbox(
            ":blue[Select Region]",
            list(REGIONS.keys())
        )
        
        # Country selection based on the region
        selected_country = st.selectbox(
            ":blue[Select Country]",
            list(REGIONS[selected_region].keys())
        )
    
    # Show coordinates in debug mode (optional)
    if use_location and isinstance(location_data, dict) and st.checkbox("🔍 Show details", value=False):
        st.info(f"""
        **Detected coordinates:**
        - Latitude: {location_data['lat']:.4f}
        - Longitude: {location_data['lon']:.4f}
        """)
    
    # Quality filter selection
    selected_quality = st.selectbox(
        ":blue[Recording Quality]",
        list(QUALITY_RATINGS.keys())
    )
    
    # Song type filter selection
    selected_type = st.selectbox(
        ":blue[Song Type]",
        list(SONG_TYPES.keys())
    )
    
    st.markdown("---")
    st.header(":blue[About]")
    st.markdown("""
        This application uses the Xeno-canto API to identify and find
        bird songs similar to the provided recording.
        
        ### :blue[About Xeno-canto]
        Xeno-canto is a collaborative database of bird recordings
        from around the world. It contains over 575,000 recordings of
        more than 10,000 species.
        
        ### :blue[How it works]
        1. Select the region and adjust the filters
        2. Upload your audio recording
        3. The application will search for similar recordings
        4. You will see a list of possible matches
        
        ### :blue[Available filters]
        - **:blue[Region and Country:]** Select from 6 continents and over 30 countries
        - **:blue[Quality:]** Filter by recording quality (A-C)
        - **:blue[Song Type:]** Specify the type of sound (song, call, etc.)
    """)

# Main content area
st.subheader("Record or upload an audio file")
st.markdown(" :blue[You can record an audio or upload an existing file (.wav, .mp3)]")

# Columns for recording and uploading a file
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Record :blue[audio]")
    if 'recording' not in st.session_state:
        st.session_state.recording = False
        st.session_state.audio_file = None
    
    # Record button
    if not st.session_state.recording:
        if st.button("Start Recording"):
            st.session_state.recording = True
            st.rerun()
    else:
        st.warning("⚡ Recording... (maximum 60 seconds)")
        duration = st.slider("Duration (seconds)", 1, MAX_DURATION, 30)
        
        if st.button("Stop Recording"):
            with st.spinner("Processing recording..."):
                # Record audio
                temp_file = record_audio(duration)
                st.session_state.audio_file = temp_file
                
                # Show player
                st.audio(temp_file)
                
                st.success("✅ Recording completed!")
                st.session_state.recording = False

with col2:
    st.subheader("📁 Upload :blue[file]")
    uploaded_file = st.file_uploader("Select an audio file", type=["wav", "mp3"])

# Use the file for search
audio_file = uploaded_file if uploaded_file else st.session_state.get('audio_file')

if audio_file:
    # Show player only for uploaded files
    if uploaded_file:
        st.audio(uploaded_file)
    
    # Search button
    if st.button("Search Matches"):
        with st.spinner(f"Searching recordings..."):
            # Progress bar
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Search for recordings
            results = search_recordings(
                REGIONS[selected_region][selected_country],
                QUALITY_RATINGS[selected_quality],
                SONG_TYPES[selected_type]
            )
            
            if results and results.get('recordings'):
                st.success("Search completed!")
                
                # Show statistics
                st.markdown(f"""
                ### :blue[Search Results]
                - **Total matches**: {len(results['recordings'])}
                - **Region**: {selected_region}
                - **Country**: {selected_country}
                - **Quality Filter**: {selected_quality}
                - **Song Type**: {selected_type}
                """)
                
                # Display results
                st.header(":blue[Recordings Found]")
                
                for idx, recording in enumerate(results['recordings'][:10]):
                    with st.expander(f"Match {idx + 1}: {recording['en']} ({recording['gen']} {recording['sp']})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            ### Recording Details
                            - **Location**: {recording.get('loc', 'Not specified')}
                            - **Date**: {recording.get('date', 'Not specified')}
                            - **Time**: {recording.get('time', 'Not specified')}
                            - **Quality**: {recording.get('q', 'Not specified')}
                            - **Type**: {recording.get('type', 'Not specified')}
                            - **Duration**: {recording.get('length', 'Not specified')}s
                            """)
                            
                            if recording.get('file'):
                                st.audio(recording['file'])
                            
                            if recording.get('remarks'):
                                st.markdown("### Notes")
                                st.write(recording['remarks'])
                        
                        with col2:
                            # Get additional species information
                            species_name = f"{recording['gen']} {recording['sp']}"
                            
                            # Wikipedia information
                            wiki_info = get_species_info(species_name)
                            if wiki_info:
                                if wiki_info['image_url']:
                                    st.image(wiki_info['image_url'], caption=wiki_info['title'])
                                st.markdown(f"[Read more on Wikipedia]({wiki_info['url']})")
                            
                            # eBird information
                            ebird_info = get_ebird_info(species_name)
                            if ebird_info:
                                st.markdown("### eBird Classification")
                                st.write(f"Order: {ebird_info.get('order', 'Unknown')}")
                                st.write(f"Family: {ebird_info.get('family', 'Unknown')}")
            else:
                st.warning("No matches found. Try adjusting your search filters.")
else:
    st.info("👆 Upload an audio file to start the analysis")

# Footer
st.markdown("---")
st.markdown(":blue[[_HarvardX CS50x_](https://cs50.harvard.edu/x/2025/)] Project :blue[|] Developed by :blue[[Darwin Paz](https://github.com/dwn10)]")