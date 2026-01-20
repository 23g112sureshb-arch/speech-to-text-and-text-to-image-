import streamlit as st
import speech_recognition as sr
from groq import Groq
import requests
from PIL import Image
from io import BytesIO
import os

# Page config
st.set_page_config(page_title="Speech to Image Generator", page_icon="🎨", layout="wide")

# Title
st.title("🎤 Speech-to-Text & Text-to-Image Generator")
st.markdown("Convert your speech to text using Groq AI, then generate images!")

# Sidebar for API keys
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Groq API Key", type="password", help="Get free API key from console.groq.com")
    hf_api_key = st.text_input("Hugging Face API Key (optional)", type="password", help="Get free API key from huggingface.co")
    st.markdown("---")
    st.markdown("### 📝 Instructions")
    st.markdown("1. Add your Groq API key")
    st.markdown("2. Record or upload audio")
    st.markdown("3. Convert speech to text")
    st.markdown("4. Generate image from text")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.header("🎤 Step 1: Speech to Text")
    
    # Audio input options
    audio_option = st.radio("Choose audio input method:", ["Upload Audio File", "Record Audio (Coming Soon)"])
    
    if audio_option == "Upload Audio File":
        audio_file = st.file_uploader("Upload an audio file (WAV, MP3, FLAC)", type=["wav", "mp3", "flac"])
        
        if audio_file and st.button("🔄 Convert Speech to Text"):
            if not groq_api_key:
                st.error("Please enter your Groq API key in the sidebar!")
            else:
                with st.spinner("Converting speech to text..."):
                    try:
                        # Initialize Groq client
                        client = Groq(api_key=groq_api_key)
                        
                        # Transcribe audio using Groq's Whisper
                        transcription = client.audio.transcriptions.create(
                            file=audio_file,
                            model="whisper-large-v3",
                            response_format="text"
                        )
                        
                        st.session_state['transcribed_text'] = transcription
                        st.success("✅ Speech converted to text!")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Display transcribed text
    if 'transcribed_text' in st.session_state:
        st.subheader("📝 Transcribed Text:")
        transcribed_text = st.text_area(
            "Edit if needed:",
            value=st.session_state['transcribed_text'],
            height=150,
            key="text_editor"
        )
        st.session_state['final_text'] = transcribed_text

with col2:
    st.header("🎨 Step 2: Text to Image")
    
    # Text input (manual or from transcription)
    if 'final_text' not in st.session_state:
        st.session_state['final_text'] = ""
    
    prompt_text = st.text_area(
        "Image prompt (auto-filled from speech or enter manually):",
        value=st.session_state.get('final_text', ''),
        height=150,
        placeholder="Describe the image you want to generate..."
    )
    
    if st.button("🎨 Generate Image"):
        if not prompt_text.strip():
            st.warning("Please provide a text prompt!")
        else:
            with st.spinner("Generating image... This may take a moment"):
                try:
                    # Using Hugging Face's free Stable Diffusion API
                    API_URL = "https://router.huggingface.co/models/stabilityai/stable-diffusion-2-1"
                    headers = {"Authorization": f"Bearer {hf_api_key}"} if hf_api_key else {}
                    
                    response = requests.post(
                        API_URL,
                        headers=headers,
                        json={"inputs": prompt_text},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        st.session_state['generated_image'] = image
                        st.success("✅ Image generated successfully!")
                    else:
                        st.error(f"Error generating image: {response.text}")
                        if "rate limit" in response.text.lower():
                            st.info("💡 Tip: Add your free Hugging Face API key in the sidebar for more requests!")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Display generated image
    if 'generated_image' in st.session_state:
        st.subheader("🖼️ Generated Image:")
        st.image(st.session_state['generated_image'], use_container_width=True)
        
        # Download button
        buf = BytesIO()
        st.session_state['generated_image'].save(buf, format="PNG")
        st.download_button(
            label="⬇️ Download Image",
            data=buf.getvalue(),
            file_name="generated_image.png",
            mime="image/png"
        )

# Footer
st.markdown("---")
st.markdown("### 🚀 How to get free API keys:")
st.markdown("- **Groq**: Visit [console.groq.com](https://console.groq.com) and sign up for free")
st.markdown("- **Hugging Face** (optional): Visit [huggingface.co](https://huggingface.co) and create a free account")