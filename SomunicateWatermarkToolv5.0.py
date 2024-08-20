import io
import numpy as np
import streamlit as st
import librosa
import soundfile as sf

def overlay(audio_files, watermark_file, volume_factor, output_format="wav"):
    watermarked_audios = []
    try:
        # Load the watermark file once
        watermark, sr_watermark = librosa.load(watermark_file, sr=None)

        # Adjust the watermark volume based on the slider value once
        watermark *= volume_factor

        for audio_file in audio_files:
            # Check if the audio_file is an uploaded file or a default string path
            if isinstance(audio_file, str):
                audio, sr_audio = librosa.load(audio_file, sr=None)
                filename = audio_file.split("/")[-1]  # Extract filename from path
            else:
                audio, sr_audio = librosa.load(audio_file, sr=None)
                filename = audio_file.name  # For uploaded files

            # Make the watermark file loop to match the length of the audio
            watermark_repeated = np.tile(watermark, int(np.ceil(len(audio) / len(watermark))))
            watermark_repeated = watermark_repeated[:len(audio)]

            # Overlay the watermark on the audio
            watermarked_audio = audio + watermark_repeated

            # Ensure audio levels are within range
            watermarked_audio = np.clip(watermarked_audio, -1.0, 1.0)

            # Export the watermarked audio to a byte stream
            output_buffer = io.BytesIO()
            sf.write(output_buffer, watermarked_audio, sr_audio, format=output_format)
            output_buffer.seek(0)  # Reset the buffer position to the beginning

            # Append to list with filename
            watermarked_audios.append((filename, output_buffer))
    except Exception as e:
        st.error(f"An error occurred while overlaying the watermark: {e}")
        return None

    return watermarked_audios

# Set the background color to black and other styles
st.markdown(
    """
    <style>
    .reportview-container {
        background: black;
        color: #8A2BE2;
    }
    .markdown-text-container {
        color: #8A2BE2;
    }
    h1 {
        color: #8A2BE2;
        font-size: 2.5em;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.2);
    }
    h3, h4 {
        color: #8A2BE2;
        font-size: 1.5em;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.2);
    }
    p {
        color: #9370DB;
        font-style: oblique;
        font-weight: bold;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI - Title at the top
st.title("Somunicate Audio Watermarking Tool")

col1, col2 = st.columns([4.0, 4.0])

with col1:
    # File uploader for multiple audio files to be watermarked
    uploaded_files = st.file_uploader("Upload audio files (multiple files allowed):", type=["wav", "mp3"], accept_multiple_files=True)

    # Default UX Sound options
    default_UX_examples = {
        "Example 1": "birds_watermark.mp3",
        "E2": "boat_in_watermark.mp3",
        "E3": "cat_watermark.mp3",
        "E4": "somunicate_watermark.mp3"
    }

    st.write("Select from our default UX sounds:")

    # Allow multiple checkbox selections from the default UX sounds
    selected_defaults = []
    for label, path in default_UX_examples.items():
        if st.checkbox(f"Add {label}"):
            selected_defaults.append(path)

    # Combine the uploaded files and selected default sounds into one list
    all_audio_files = list(uploaded_files or []) + selected_defaults

    # Output the final list for confirmation
    if all_audio_files:
        st.write(f"Total audio files to be watermarked: {len(all_audio_files)}")

with col2:
    # Checkbox to decide if custom watermark is uploaded
    custom_wm_check = st.checkbox("Upload Custom Watermark?")
    
    # Default watermark options
    default_watermarks = {
        "birds watermark": "birds_watermark.mp3",
        "boat in watermark": "boat_in_watermark.mp3",
        "cat watermark": "cat_watermark.mp3",
        "somunicate-watermark": "somunicate_watermark.mp3"
    }

    uploaded_watermark = None  # Initialize the uploaded watermark variable

    if custom_wm_check:
        # File uploader for the watermark file
        uploaded_watermark = st.file_uploader("Upload a watermark file:", type=["wav", "mp3"])
    else:
        st.write("Select from our default watermarks:")
        
        # Radio button for selecting one of the default watermarks
        selected_watermark = st.radio("Default watermarks", list(default_watermarks.keys()))
        
        if selected_watermark:
            watermark_path = default_watermarks[selected_watermark]
            st.audio(watermark_path, format='audio/mp3')
            uploaded_watermark = watermark_path

# Slider to adjust watermark volume
volume_factor = st.slider("Adjust watermark volume:", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

st.write("Watermarked Sounds Display and Download: ")
# Proceed if both audio files and a watermark are provided
if all_audio_files and uploaded_watermark:
    # Overlay watermark
    watermarked_audios = overlay(all_audio_files, uploaded_watermark, volume_factor)

    if watermarked_audios:
        for filename, output_buffer in watermarked_audios:
            # Create a playback button for each watermarked audio file
            st.audio(output_buffer, format='audio/wav')
            st.write(f"Watermarked {filename}")
