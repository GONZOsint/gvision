import io
import cv2
import numpy as np
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

# Add a button to display the readme.md file in a popup
if st.sidebar.checkbox('README'):
    with open('readme.md', 'r', encoding='UTF-8') as f:
        readme = f.read()
    st.info(readme)

# Set sidebar title and description
st.sidebar.title('ℹ️ About')
st.sidebar.info('GVision is a reverse image search app that use Google Cloud Vision API to detect landmarks and web entities from images, helping you gather valuable information quickly and easily.')
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
        st.sidebar.subheader('🖼️ Supported image formats:')
        st.sidebar.markdown("""
                - JPG
                - JPEG
                - PNG
            """)
        st.sidebar.markdown('----')
        st.sidebar.subheader('⚠️ Free: first 1000 units/month')
        st.sidebar.markdown('----')
        st.sidebar.subheader('📘 Resources:')
        st.sidebar.markdown("""
                - Cloud Vision API Documentation
                - Cloud Vision API Pricing
                ----
            """)
        st.sidebar.button('Reset app')

        # Upload image
        uploaded_file = st.file_uploader('Choose an image', type=['jpg', 'jpeg', 'png'], accept_multiple_files=False)

        def create_folium_map(landmarks):
            providers = xyz.flatten()
            selection = [
                'OpenTopoMap',
                'Stadia.AlidadeSmooth',
                'Stadia.AlidadeSmoothDark',
                'Stadia.OSMBright',
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
                zoom_start=15
            )

            for landmark in landmarks:
                tooltip = landmark.description
                folium.Marker(
                    location=[landmark.locations[0].lat_lng.latitude, landmark.locations[0].lat_lng.longitude],
                    tooltip=tooltip
                ).add_to(m)

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
                content = uploaded_file.read()
                image = types.Image(content=content)
                response = client.landmark_detection(image=image)
                landmarks = response.landmark_annotations

                st.write('-------------------')
                st.subheader('📤 Uploaded image and detected location:')
                col1, col2 = st.columns(2)
                with col1:
                    image = Image.open(io.BytesIO(content))
                    st.image(image, use_container_width=True, caption='')
                if landmarks:
                    with col2:
                        folium_map = create_folium_map(landmarks)
                        folium_static(folium_map)
                    st.write('-------------------')
                    st.subheader('📍 Location information:')
                    for landmark in landmarks:
                        st.write('- **Coordinates**: ' + str(landmark.locations[0].lat_lng.latitude) + ', ' + str(landmark.locations[0].lat_lng.longitude))
                        st.write('- **Location**: ' + landmark.description)
                        st.write('')
                    st.write('-------------------')
                else:
                    st.write('❌ No landmarks detected.')
                    st.write('-------------------')

                image = types.Image(content=content)
                response = client.logo_detection(image=image)
                logos_detected = response.logo_annotations

                if logos_detected:
                    st.subheader('👓 Logos Detected:')
                    for logo in logos_detected:
                        st.markdown(f'''- {logo.description}''')
                else:
                    st.write('❌ No Logos Detected.')
                st.write('-------------------')

                image = types.Image(content=content)
                response = client.object_localization(image=image)
                object_annotations = response.localized_object_annotations

                if object_annotations:
                    st.subheader('🧳 Objects Detected:')
                    annotated_image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
                    if annotated_image is not None:
                        for object_found in object_annotations:
                            vertices = [(int(vertex.x * annotated_image.shape[1]), int(vertex.y * annotated_image.shape[0]))
                                        for vertex in object_found.bounding_poly.normalized_vertices]
                            for i in range(len(vertices)):
                                cv2.line(annotated_image, vertices[i], vertices[(i + 1) % len(vertices)], color=(0, 255, 0), thickness=2)
                            cv2.putText(annotated_image, f"{object_found.name} ({round(object_found.score * 100, 1)}% Confidence)", (vertices[0][0], vertices[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
                        st.image(annotated_image, channels="RGB")
                    else:
                        st.write('❌ Error loading image for object detection.')
                else:
                    st.write('❌ No Objects Detected.')
                st.write('-------------------')

                image = types.Image(content=content)
                response = client.web_detection(image=image)
                web_entities = response.web_detection.web_entities
                pages_with_matching_images = response.web_detection.pages_with_matching_images
                visually_similar_images = response.web_detection.visually_similar_images

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
                                st.image(image.url, use_container_width=True, caption=image.url)
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
