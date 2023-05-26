![alt gvision_1](https://imgur.com/KnxDEKq.png)

GVision is a reverse image search app that use Google Cloud Vision API to detect landmarks and web entities from images, helping you gather valuable information quickly and easily.


https://user-images.githubusercontent.com/37483725/228700363-cc0d8131-4134-4f37-918e-1a342dd22b83.mp4




## 🤖 About Google Cloud Vision API

Google Cloud Vision API is a machine learning-powered image analysis service that provides developers with tools to understand the contents of an image. It can detect objects, faces, text, logos, and more within an image.




## 🚀 Getting Started

Before using the app, you need to obtain a Google Cloud Vision API key.

- Go to the [Google Cloud Platform Console](https://console.cloud.google.com/).
- Create a new project or select an existing one.
- Enable the Cloud Vision API for your project.
- Create a service account and download a private key in JSON format.
- Upload your Google Cloud Vision API key in JSON format by clicking on the `Upload a config file` button in the sidebar.


## 🌐 Running online

🔗 App: https://gvision.streamlit.app


## 🛠️ Installation

To install the dependencies, simply run the following command:

`pip install -r requirements.txt`


## 🏃‍♀ Running the app

You can run the app locally by running the following command:

`streamlit run gvision.py`


## 🔎 Usage

Using GVision is simple and straightforward:

- Upload your Google Cloud Vision API key in JSON format by clicking on the `Upload a config file` button in the sidebar.
- Once the key is uploaded, the app will automatically authenticate with the Google Cloud Vision API.
- Upload an image in JPG, JPEG, or PNG format by clicking on the `Choose an image` button.
- Wait for the app to analyze the image. The app will detect landmarks and web entities present in the image and display them on a map.
- Choose between the different tile options to view the detected landmarks and web entities.

You can also find links to the Google Cloud Vision API documentation and pricing in the `Resources` section of the sidebar. 

To reset the app to its default state or to clear the uploaded image and results, click on the `Reset app` button.


## 📚 Resources

- [Google Cloud Vision API Documentation](https://cloud.google.com/vision/docs)
- [Google Cloud Vision API Pricing](https://cloud.google.com/vision/pricing)




## 📢 Mentions

- @PierrunoYT (https://github.com/PierrunoYT/photo-location-finder)
