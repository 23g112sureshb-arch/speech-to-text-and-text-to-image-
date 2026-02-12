import streamlit as st
from groq import Groq
from PIL import Image
from io import BytesIO
import requests
import urllib.parse

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Speech to Image Generator",
    page_icon="🎨",
    layout="wide"
)

st.title("🎤 Speech-to-Text ➜ Text-to-Image Generator")
st.markdown("Convert speech to text using Groq, then generate AI images!")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("🔑 API Configuration")
    groq_api_key = st.text_input("Groq API Key", type="password")
    st.markdown("---")
    st.markdown("### How to get keys:")
    st.markdown("• Groq → https://console.groq.com")

# ---------------- LAYOUT ----------------
col1, col2 = st.columns(2)

# =====================================================
# 🎤 SPEECH TO TEXT
# =====================================================
with col1:
    st.header("Step 1: Speech to Text")

    audio_file = st.file_uploader(
        "Upload Audio File (wav, mp3, flac)",
        type=["wav", "mp3", "flac"]
    )

    if st.button("Convert Speech to Text"):
        if not groq_api_key:
            st.error("Please enter your Groq API key.")
        elif not audio_file:
            st.warning("Please upload an audio file.")
        else:
            try:
                with st.spinner("Transcribing..."):
                    client = Groq(api_key=groq_api_key)
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_file.getvalue()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    st.session_state["transcribed_text"] = transcription
                st.success("✅ Transcription completed!")
            except Exception as e:
                st.error(f"Error: {e}")

    if "transcribed_text" in st.session_state:
        st.subheader("Transcribed Text")
        edited_text = st.text_area(
            "Edit if needed:",
            value=st.session_state["transcribed_text"],
            height=150
        )
        st.session_state["final_prompt"] = edited_text

# =====================================================
# 🎨 TEXT TO IMAGE (Pollinations AI)
# =====================================================
with col2:
    st.header("Step 2: Generate Image")

    prompt = st.text_area(
        "Image Prompt:",
        value=st.session_state.get("final_prompt", ""),
        height=150
    )

    if st.button("Generate Image"):
        if not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            try:
                with st.spinner("Generating image..."):
                    # Encode prompt for URL
                    encoded_prompt = urllib.parse.quote(prompt)
                    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

                    response = requests.get(url)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        st.image(image, use_container_width=True)
                        st.success("✅ Image generated successfully!")

                        # Download button
                        buf = BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button(
                            label="⬇️ Download Image",
                            data=buf.getvalue(),
                            file_name="generated_image.png",
                            mime="image/png"
                        )
                    else:
                        st.error(f"Error generating image. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("Built with ❤️ using Groq + Pollinations AI + Streamlit")
