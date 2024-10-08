import io
import numpy as np
import streamlit as st
import librosa
import soundfile as sf
from scipy.signal import chirp

def overlay(audio_files, watermark_file, volume_factor, output_format="wav"):
    watermarked_audios = []
    try:
        # Load the watermark file once
        watermark, sr_watermark = librosa.load(watermark_file, sr=None)

        # Adjust the watermark volume based on the slider value
        watermark *= volume_factor

        # Extract the first 0.5 seconds of the watermark
        prepend_duration = 0.5  # 0.5 seconds
        prepend_samples = int(prepend_duration * sr_watermark)
        watermark_prepend = watermark[:prepend_samples]

        # Modulate the watermark frequency to decrease over time
        time = np.linspace(0, len(watermark) / sr_watermark, len(watermark))
        decreasing_tone = chirp(time, f0=1000, f1=100, t1=time[-1], method='linear')
        watermark *= decreasing_tone

        for audio_file in audio_files:
            # Load the audio file
            if isinstance(audio_file, str):
                audio, sr_audio = librosa.load(audio_file, sr=None)
                filename = audio_file.split("/")[-1]
            else:
                audio, sr_audio = librosa.load(audio_file, sr=None)
                filename = audio_file.name

            # Resample the audio if the sample rates don't match
            if sr_audio != sr_watermark:
                audio = librosa.resample(audio, orig_sr=sr_audio, target_sr=sr_watermark)
                sr_audio = sr_watermark  # Now they have the same sample rate

            # Repeat the watermark to match the length of the audio (excluding the prepend part)
            watermark_repeated = np.tile(watermark, int(np.ceil(len(audio) / len(watermark))))
            watermark_repeated = watermark_repeated[:len(audio)]

            # Combine the 0.5 seconds of watermark with the audio
            combined_audio = np.concatenate((watermark_prepend, audio))

            # Overlay the watermark on the combined audio
            watermarked_audio = combined_audio + np.concatenate((watermark_prepend, watermark_repeated))

            # Ensure audio levels are within range
            watermarked_audio = np.clip(watermarked_audio, -1.0, 1.0)

            # Export the watermarked audio to a byte stream
            output_buffer = io.BytesIO()
            sf.write(output_buffer, watermarked_audio, sr_audio, format=output_format)
            output_buffer.seek(0)

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

# Using HTML and CSS for centering the title
st.markdown(
    """
    <h1 style='text-align: center;'>Somunicate Audio Watermarking Tool</h1>
    """, 
    unsafe_allow_html=True
)

col1, col2 = st.columns([4.0, 4.0])

with col1:
    # File uploader for multiple audio files to be watermarked
    uploaded_files = st.file_uploader("Upload audio files (multiple files allowed):", type=["wav", "mp3"], accept_multiple_files=True)

    # Default UX Sound options
    default_UX_examples = {
        "Example 1": "googleOk_apps-005.mp3",
        "E2": "JBL_Consumer-003.mp3",
        "E3": "nintendo_switch_consumer-010.mp3",
        "E4": "Samsung_One_Apps-004.mp3"
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
        "Birds Watermark": "birds_watermark.mp3",
        "Boat Watermark": "boat_in_watermark.mp3",
        "Cat Watermark": "cat_watermark.mp3",
        "Somunicate Watermark": "somunicate_watermark.mp3",
        "Pink Noise": "07-PinkNoise.mp3"
    }

    uploaded_watermark = None  # Initialize the uploaded watermark variable

    if custom_wm_check:
        # File uploader for the watermark file
        uploaded_watermark = st.file_uploader("Upload a watermark file:", type=["wav", "mp3"])
    else:  
        # Radio button for selecting one of the default watermarks
        selected_watermark = st.radio("Select from our default watermarks:", list(default_watermarks.keys()))
        
        if selected_watermark:
            watermark_path = default_watermarks[selected_watermark]
            st.audio(watermark_path, format='audio/mp3')
            uploaded_watermark = watermark_path

# Slider to adjust watermark volume
volume_factor = st.slider("Adjust watermark volume:", min_value=0.0, max_value=2.0, value=0.01, step=0.01)

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