import io
import streamlit as st
from google.cloud import vision
from google.cloud.vision_v1 import types
from google.oauth2 import service_account
from streamlit_folium import folium_static
import folium
from PIL import Image
import xyzservices.providers as xyz
import json

# Set page style
st.set_page_config(page_title='GVision', page_icon='📷', layout='wide')

# Set page logo
logo_path = "gvision.png"
logo = Image.open(logo_path)

st.image(logo, width=320)

# Add a button to display the readme.md file in a popup
if st.sidebar.checkbox('README'):
    with open('readme.md', 'r', encoding='UTF-8') as f:
        readme = f.read()
    st.info(readme)

# Set sidebar title and description
st.sidebar.title('ℹ️ About')
st.sidebar.info('GVision is a reverse image search app designedthat use Google Cloud Vision API to detect landmarks and web entities from images, helping you gather valuable information quickly and easily.')
st.sidebar.markdown('----')

# Add a button to upload a config file
config_slot = st.empty()
config_file = config_slot.file_uploader('Upload a config file', type=['json'])

# Load the credentials from the config file
if config_file is not None:
    content = config_file.read()
    try:
        credentials = service_account.Credentials.from_service_account_info(json.loads(content))
        client = vision.ImageAnnotatorClient(credentials=credentials)
        config_slot.empty()
        # Add examples of supported image formats, sizes, and resolutions
        st.sidebar.subheader('🖼️ Supported image formats:')
        st.sidebar.markdown("""
                - JPG
                - JPEG
                - PNG
            """)
        st.sidebar.markdown('----')

        # Add free tier data
        st.sidebar.subheader('⚠️ Free: first 1000 units/month')
        st.sidebar.markdown('----')

        # Provide a link or reference to the Google Cloud Vision API documentation or pricing
        st.sidebar.subheader('📘 Resources:')
        st.sidebar.markdown("""
                - [Cloud Vision API Documentation](https://cloud.google.com/vision/docs)
                - [Cloud Vision API Pricing](https://cloud.google.com/vision/pricing)
                ----
            """)

        # Add a button to reset the app to its default state or to clear the uploaded image and results
        st.sidebar.button('Reset app')

        # Upload image
        uploaded_file = st.file_uploader('Choose an image', type=['jpg', 'jpeg', 'png'], accept_multiple_files=False)

        def create_folium_map(landmarks):
            providers = xyz.flatten()
            selection = ['OpenTopoMap',
                         'Stamen.Toner',
                         'Stamen.Terrain',
                         'Stamen.TerrainBackground',
                         'Stamen.Watercolor',
                         'CartoDB.Positron',
                         'CartoDB.Voyager',
                         'WaymarkedTrails.hiking',
                         'WaymarkedTrails.cycling',
                         'WaymarkedTrails.mtb',
                         'WaymarkedTrails.slopes',
                         'WaymarkedTrails.riding',
                         'WaymarkedTrails.skating'
                         ]

            # Create a map centered on the first detected location using Folium
            m = folium.Map(
                location=[landmarks[0].locations[0].lat_lng.latitude, landmarks[0].locations[0].lat_lng.longitude],
                zoom_start=15)

            for landmark in landmarks:
                # Add a marker to the existing map for each detected location
                tooltip = landmark.description
                folium.Marker(
                    location=[landmark.locations[0].lat_lng.latitude, landmark.locations[0].lat_lng.longitude],
                    tooltip=tooltip).add_to(m)
            for tiles_name in selection:
                tiles = providers[tiles_name]
                folium.TileLayer(
                    tiles=tiles.build_url(),
                    attr=tiles.html_attribution,
                    name=tiles.name,
                ).add_to(m)
            folium.LayerControl().add_to(m)
            return m


        if uploaded_file is not None:
            with st.spinner('Analyzing the image...'):
                # Read the image file
                content = uploaded_file.read()
                # Perform landmark detection on the image
                image = types.Image(content=content)
                response = client.landmark_detection(image=image)

                # Extract the detected landmarks and their geolocation
                landmarks = response.landmark_annotations

                # Show the uploaded image and map side-by-side
                st.write('-------------------')
                st.subheader('📤 Uploaded image and detected location:')
                col1, col2 = st.columns(2)
                with col1:
                    image = Image.open(io.BytesIO(content))
                    st.image(image, use_column_width=True, caption='')
                if landmarks:
                    with col2:
                        # Create a map centered on the first detected location using Folium
                        providers = xyz.flatten()
                        selection = [
                            'OpenTopoMap',
                            'Stamen.Toner',
                            'Stamen.Terrain',
                            'Stamen.TerrainBackground',
                            'Stamen.Watercolor',
                            'CartoDB.Positron',
                            'CartoDB.Voyager',
                            'WaymarkedTrails.hiking',
                            'WaymarkedTrails.cycling',
                            'WaymarkedTrails.mtb',
                            'WaymarkedTrails.slopes',
                            'WaymarkedTrails.riding',
                            'WaymarkedTrails.skating',
                            'OpenRailwayMap'
                        ]

                        m = folium.Map(
                            location=[landmarks[0].locations[0].lat_lng.latitude, landmarks[0].locations[0].lat_lng.longitude],
                            zoom_start=15)

                        for landmark in landmarks:
                             # Add a marker to the existing map for each detected location
                            tooltip = landmark.description
                            folium.Marker(
                                location=[landmark.locations[0].lat_lng.latitude, landmark.locations[0].lat_lng.longitude],
                                tooltip=tooltip).add_to(m)
                        for tiles_name in selection:
                            tiles = providers[tiles_name]
                            folium.TileLayer(
                                tiles=tiles.build_url(),
                                attr=tiles.html_attribution,
                                name=tiles.name,
                            ).add_to(m)
                        folium.LayerControl().add_to(m)
                        folium_static(m)
                    st.write('-------------------')
                    st.subheader('📍 Location information:')
                    for landmark in landmarks:
                        st.write('- **Coordinates**: ' + str(landmark.locations[0].lat_lng.latitude) + ', ' + str(
                            landmark.locations[0].lat_lng.longitude))
                        st.write('- **Location**: ' + landmark.description)
                        st.write('')
                    st.write('-------------------')
                else:
                    st.write('❌ No landmarks detected.')
                    st.write('-------------------')


                # Perform web detection on the image
                image = types.Image(content=content)
                response = client.web_detection(image=image)

                # Extract the detected web entities and pages
                web_entities = response.web_detection.web_entities
                pages_with_matching_images = response.web_detection.pages_with_matching_images
                visually_similar_images = response.web_detection.visually_similar_images

                # Print the detected web entities and pages
                if web_entities or pages_with_matching_images or visually_similar_images:
                    st.subheader('🌐 Detected web entities:')
                    entity_rows = [entity.description for entity in web_entities if entity.description]
                    if entity_rows:
                        st.write(entity_rows)
                    else:
                        st.write('❌ No web entities detected.')
                    st.write('-------------------')

                    st.subheader('🔗 Pages with matching images:')
                    page_rows = [page.url for page in pages_with_matching_images]
                    if page_rows:
                        st.write(page_rows)
                    else:
                        st.write('❌ No pages with matching images found.')
                    st.write('-------------------')

                    st.subheader('🖼️ Visually similar images:')
                    similar_images = [image for image in visually_similar_images if image.url]
                    num_images = len(similar_images)
                    if num_images > 0:
                        cols = st.columns(3)
                        for i, image in enumerate(similar_images):
                            if i % 3 == 0:
                                cols = st.columns(3)
                            with cols[i % 3]:
                                st.image(image.url, use_column_width=True, caption=image.url)
                    else:
                        st.write('❌ No visually similar images found.')
                else:
                    st.write('❌ No web entities detected.')
        else:
            st.write('📁 Please upload an image.')
        config_slot.empty()
    except json.JSONDecodeError as e:
        st.error("Invalid JSON syntax in config file: {}".format(e))
    except Exception as e:
        st.error("Error while loading config file: {}".format(e))
    config_slot.empty()
else:
    st.warning('Please upload a config file.')
