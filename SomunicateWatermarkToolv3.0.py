import io
import numpy as np
import streamlit as st
import librosa
import soundfile as sf

# Display NumPy version for debugging
st.write(f"NumPy version: {np.__version__}")

def overlay(audio_files, watermark_file, volume_factor, output_format="wav"):
    watermarked_audios = []
    st.write("TESTING")
    try:
        # Load the watermark file once
        watermark, sr_watermark = librosa.load(watermark_file, sr=None)

        for audio_file in audio_files:
            # Load the audio file
            audio, sr_audio = librosa.load(audio_file, sr=None)

            # Ensure that the sampling rates are the same
            if sr_audio != sr_watermark:
                st.error("Sampling rates of audio and watermark files must be the same.")
                return None

            # Make the watermark file loop to match the length of the audio
            num_repeats = int(np.ceil(len(audio) / len(watermark)))
            watermark = np.tile(watermark, num_repeats)[:len(audio)]

            # Adjust the watermark volume based on the slider value
            watermark *= volume_factor

            # Overlay the watermark on the audio
            watermarked_audio = np.add(audio, watermark)  # Use np.add for compatibility

            # Ensure audio levels are within range
            watermarked_audio = np.clip(watermarked_audio, -1.0, 1.0)

            # Export the watermarked audio to a byte stream
            output_buffer = io.BytesIO()
            sf.write(output_buffer, watermarked_audio, sr_audio, format=output_format)
            output_buffer.seek(0)  # Reset the buffer position to the beginning

            # Append to list with filename
            watermarked_audios.append((audio_file.name, output_buffer))
    except Exception as e:
        st.error(f"An error occurred while overlaying the watermark: {e}")
        return None

    return watermarked_audios

# Streamlit UI
st.title("Audio Watermarking Tool")

# File uploader for multiple audio files
uploaded_files = st.file_uploader("Upload audio files (multiple files allowed):", type=["wav", "mp3"], accept_multiple_files=True)

# File uploader for the watermark file
uploaded_watermark = st.file_uploader("Upload a watermark file:", type=["wav", "mp3"])

# Slider to adjust watermark volume
volume_factor = st.slider("Adjust watermark volume:", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

if uploaded_files and uploaded_watermark:
    # Overlay watermark
    watermarked_audios = overlay(uploaded_files, uploaded_watermark, volume_factor)

    if watermarked_audios:
        for filename, output_buffer in watermarked_audios:
            # Create a download button for each watermarked audio file
            st.download_button(
                label=f"Download watermarked {filename}",
                data=output_buffer,
                file_name=f"watermarked_{filename}",
                mime='audio/wav'
            )
