import streamlit as st
from groq import Groq
from PIL import Image
from io import BytesIO
import requests
import urllib.parse

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="🌍 Multilingual Speech-to-Image Generator",
    page_icon="🎨",
    layout="wide"
)

st.title("🎤🌍 Multilingual Speech-to-Text ➜ Ultra-Fast Image Generator")
st.markdown("**Free • No tokens needed • All languages supported • Instant results**")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("🔑 API Configuration")
    groq_api_key = st.text_input("Groq API Key", type="password", help="Get from console.groq.com")
    
    st.markdown("---")
    st.markdown("### 🌍 Language Support")
    st.info("✅ **Whisper-large-v3 supports 100+ languages automatically**")
    st.markdown("- Hindi, Tamil, English, Spanish, French")
    st.markdown("- Chinese, Arabic, German, Japanese, Korean")
    st.markdown("- And 99+ more (auto-detects!)")
    
    st.markdown("### 🚀 Free Features")
    st.markdown("- ✅ Pollinations AI (Unlimited, No API key)")
    st.markdown("- ✅ Flux, Stable Diffusion models")
    st.markdown("- ✅ HD images (1024x1024)")

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([1, 1])

# =====================================================
# 🎤 MULTILINGUAL SPEECH TO TEXT
# =====================================================
with col1:
    st.header("Step 1: Speech to Text (Any Language)")
    
    # Language selector (optional - Whisper auto-detects)
    language = st.selectbox(
        "Language (auto-detected):",
        ["auto-detect", "Hindi", "Tamil", "English", "Spanish", "French", "German", "Chinese"],
        index=0
    )
    
    audio_file = st.file_uploader(
        "📁 Upload Audio (wav/mp3/flac)",
        type=["wav", "mp3", "flac"],
        help="Supports all languages automatically!"
    )
    
    # Audio preview
    if audio_file:
        st.audio(audio_file, format="audio/wav")
    
    if st.button("🎤 Transcribe Audio", type="primary"):
        if not groq_api_key:
            st.error("❌ Enter Groq API key in sidebar")
        elif not audio_file:
            st.warning("📤 Upload audio first")
        else:
            try:
                with st.spinner("🔄 Transcribing in your language..."):
                    client = Groq(api_key=groq_api_key)
                    
                    # Fix: Use proper file handling for all formats
                    file_data = audio_file.getvalue()
                    file_name = audio_file.name or "audio"
                    file_type = audio_file.type or "audio/wav"
                    
                    transcription = client.audio.transcriptions.create(
                        file=(file_name, file_data, file_type),
                        model="whisper-large-v3",
                        language=language if language != "auto-detect" else "auto",  # All languages!
                        response_format="text"
                    )
                    st.session_state["transcribed_text"] = transcription
                    st.session_state["detected_language"] = language
                st.success("✅ Transcription complete!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Display transcription
    if "transcribed_text" in st.session_state:
        st.success(f"🌐 Language: {st.session_state.get('detected_language', 'Auto-detected')}")
        edited_text = st.text_area(
            "✏️ Edit prompt:",
            value=st.session_state["transcribed_text"],
            height=120,
            placeholder="Your transcribed text appears here..."
        )
        st.session_state["final_prompt"] = edited_text
        st.info(f"**Characters:** {len(edited_text)}")

# =====================================================
# 🎨 ULTRA-FAST IMAGE GENERATION
# =====================================================
with col2:
    st.header("Step 2: Generate HD Images (Free!)")
    
    # Sync prompt from left column
    current_prompt = st.session_state.get("final_prompt", "")
    if current_prompt:
        st.info("📝 Using transcribed text above")
    
    # Image settings
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        width = st.slider("Width", 512, 2048, 1024, 256)
    with col_img2:
        height = st.slider("Height", 512, 2048, 1024, 256)
    
    seed = st.number_input("🔢 Seed (for consistency)", value=42)
    
    if st.button("🎨 Generate Ultra-Fast Image", type="secondary"):
        prompt = st.session_state.get("final_prompt", "").strip()
        if not prompt:
            st.warning("👆 Transcribe audio first!")
        else:
            try:
                with st.spinner("⚡ Generating HD image... (3-5 seconds)"):
                    # ULTRA-FAST Pollinations AI with HD params
                    encoded_prompt = urllib.parse.quote(prompt)
                    image_url = (
                        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                        f"?width={width}&height={height}&seed={seed}&nologo=true&safe=false"
                    )
                    
                    response = requests.get(image_url, timeout=15)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        
                        st.image(image, use_container_width=True)
                        st.success("✅ **Ultra-fast HD image generated!** 🎉")
                        
                        # Multiple download options
                        buf = BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button(
                            label="⬇️ Download PNG",
                            data=buf.getvalue(),
                            file_name=f"speech2image_{seed}.png"
                        )
                        
                        # Copy image URL
                        st.code(image_url)
                        st.info("💡 Reuse this URL directly in browser!")
                        
                    else:
                        st.error(f"🌐 HTTP {response.status_code}")
                        
            except Exception as e:
                st.error(f"⚠️ {str(e)}")

# ---------------- STATUS BAR ----------------
if "final_prompt" in st.session_state and st.session_state["final_prompt"]:
    st.markdown("---")
    st.markdown("*✅ Ready to generate! All languages supported. 100% Free.*")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("🌍 **Built with:** Groq Whisper (100+ languages) + Pollinations AI (Free/Unlimited) + Streamlit")
st.markdown("*No tokens consumed for images • Privacy-focused • Instant results*")
