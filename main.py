import streamlit as st

from src.chat import stream_local_completion
from src.media import download_social_video, transcribe_wav

# --- Page Setup ---
st.set_page_config(
    page_title="Video Downloader & Note Generator", page_icon="🎬", layout="wide"
)

# --- Session State Initialization ---
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "audio_text" not in st.session_state:
    st.session_state.audio_text = None

st.title("🎬 Video Downloader & Note Generator")
st.caption(
    "Download social media videos, extract transcriptions, and generate automated notes."
)

st.divider()

# --- Main Layout ---
col_left, col_right = st.columns([1, 1], gap="large")

# --- Left Column: Controls & Input ---
with col_left:
    with st.container(border=True):
        st.subheader("1. Download & Process Media")

        url = st.text_input(
            "Enter Video URL", placeholder="https://example.com/video.mp4"
        )

        if st.button("Download and Process", type="primary", use_container_width=True):
            if not url or not url.startswith(("http://", "https://")):
                st.error(
                    "Please enter a valid URL (must start with http:// or https://)"
                )
            else:
                with st.status("Processing media...", expanded=True) as status:
                    st.write("Downloading video...")
                    downloaded_path = download_social_video(url)

                    if downloaded_path:
                        st.session_state.video_path = downloaded_path
                        st.write("Transcribing audio...")

                        transcription = transcribe_wav(str(downloaded_path))
                        if transcription:
                            st.session_state.audio_text = transcription
                            status.update(
                                label="Processing complete!",
                                state="complete",
                                expanded=False,
                            )
                            st.success(
                                "Video and transcription successfully processed!"
                            )
                        else:
                            st.session_state.audio_text = None
                            status.update(label="Transcription failed.", state="error")
                            st.error("Failed to extract transcription from the audio.")
                    else:
                        st.session_state.video_path = None
                        st.session_state.audio_text = None
                        status.update(label="Download failed.", state="error")
                        st.error("Failed to download video from the provided URL.")

    # Show Note Generation Section only when video_path AND audio_text exist
    if st.session_state.video_path and st.session_state.audio_text:
        with st.container(border=True):
            st.subheader("2. AI Note Generator")

            if st.button("Generate Summary Note", use_container_width=True):
                st.markdown("### 📝 Generated Notes")
                try:
                    note = stream_local_completion(
                        context=st.session_state.audio_text,
                        model_name="unsloth\\LFM2_5-230M-IQ4_XS",
                    )
                    st.write_stream(note)
                except Exception as e:
                    st.error(f"Error generating notes. Please try again. Details: {e}")

# --- Right Column: Preview & Output ---
with col_right, st.container(border=True):
    st.subheader("Media Preview & Transcription")

    # Dual check for video_path and audio_text availability
    if st.session_state.video_path and st.session_state.audio_text:
        # Display Video
        st.video(st.session_state.video_path.with_suffix(".mp4"))

        # Display Transcription inside an expandable viewer
        with st.expander("📄 View Extracted Transcription", expanded=True):
            st.text_area(
                label="Audio Text",
                value=st.session_state.audio_text,
                height=200,
                disabled=True,
                label_visibility="collapsed",
            )
    else:
        st.info(
            "No active media loaded. Paste a valid video URL on the left and click **Download and Process**."
        )
