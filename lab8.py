import streamlit as st
from openai import OpenAI
import requests
import base64

client = OpenAI()

if "url_response" not in st.session_state:
    st.session_state.url_response = None

if "upload_response" not in st.session_state:
    st.session_state.upload_response = None

st.title("Image Captioning Bot")
st.write("This app generates image descriptions and possible captions from either an image URL or an uploaded image file.")

st.header("Image URL Input")
st.caption("The URL must link directly to an image file to work correctly.")

url = st.text_input("Enter image URL:")

if st.button("Generate Caption from URL") and url:
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error("Invalid image URL.")
        else:
            url_response = client.chat.completions.create(
                model="gpt-4.1-mini",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": url,
                                    "detail": "auto"
                                }
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Describe the image in at least 3 sentences. "
                                    "Write five different captions for this image. "
                                    "Captions must vary in length, minimum one word but be no longer than 2 sentences. "
                                    "Captions should vary in tone, such as funny, intellectual, and aesthetic."
                                )
                            }
                        ]
                    }
                ]
            )
            st.session_state.url_response = url_response.choices[0].message.content
    except Exception as e:
        st.error(e)

if st.session_state.url_response:
    st.image(url, caption="Image from URL", use_container_width=True)
    st.write(st.session_state.url_response)

st.header("File Upload")
st.write("Upload an image file to generate a description and captions.")

uploaded = st.file_uploader(
    "Upload an image file:",
    type=["jpg", "jpeg", "png", "webp", "gif"]
)

if st.button("Generate Caption from Upload") and uploaded:
    try:
        b64 = base64.b64encode(uploaded.read()).decode("utf-8")
        mime = uploaded.type
        data_uri = f"data:{mime};base64,{b64}"

        upload_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_uri,
                                "detail": "low"
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "Describe the image in at least 3 sentences. "
                                "Write five different captions for this image. "
                                "Captions must vary in length, minimum one word but be no longer than 2 sentences. "
                                "Captions should vary in tone, such as funny, intellectual, and aesthetic."
                            )
                        }
                    ]
                }
            ]
        )
        st.session_state.upload_response = upload_response.choices[0].message.content
    except Exception as e:
        st.error(e)

if st.session_state.upload_response:
    st.image(uploaded, caption="Uploaded Image", use_container_width=True)
    st.write(st.session_state.upload_response)