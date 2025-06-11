import io
import shutil
import numpy as np
import streamlit as st
import os
import librosa as lib
import matplotlib.pyplot as plt
import json
import soundfile as sf

#take in valid folder intput
def get_folder_path():
    folder_path = st.text_input("Enter the folder path for desired samples!")
    if os.path.exists(folder_path):
        st.success("Folder path is valid!")
    elif folder_path == "":
        st.write("No path Entered")
    elif os.path.exists(folder_path) == False:
        st.error("Folder path is not valid!")
    return folder_path
            
#scan for supported audio sample files
def scan_for_audio_files(folder_path):
    supported_formats = ('.wav', '.mp3', '.flac')
    audio_files = []
    for root, dirs, files in os.walk(folder_path):
        for item in files:
            full_path = os.path.join(root, item)
            if item.endswith(supported_formats):
                audio_files.append(full_path)
            else:
                unsupported_items = []
                unsupported_items.append(item)
                
    return audio_files
  
#sort the audio files
def sort_supported_audio_files(audio_files):
    sorted_files = sorted(audio_files)
    return sorted_files

#display supported samples selection box
def selected_from_sorted_sample_list(sorted_files):
    if sorted_files:
        selected_file = st.selectbox("These files are supported. Choose a sample:", sorted_files)
        st.write(f"Selected file: {os.path.basename(selected_file)}")
        return selected_file
        
    return None

#spectrum
def display_waveform(selected_file):
    st.subheader("Original Sample Waveform")
    y, sr = lib.load(selected_file, sr=None)
    fig, ax = plt.subplots()
    ax.plot(y)
    ax.set_title("Sample Waveform")
    st.pyplot(fig)

#note detection
def spectrum_analysis(selected_file):
    st.subheader("Original Sample Spectrum Analysis")
    y, sr = lib.load(selected_file)
    D = np.abs(lib.stft(y))
    db_spectrum = lib.amplitude_to_db(D, ref=np.max)
    avg_spectrum = db_spectrum.mean(axis=1)
    freqs = lib.fft_frequencies(sr=sr)
    fig, ax = plt.subplots()
    ax.semilogx(freqs, avg_spectrum)
    ax.set(title="General Frequency Spectrum", xlabel="Frequency (Hz)", ylabel="Amplitude (dB)")
    ax.set_xlim([20, sr // 2])  # limit from 20 Hz to Nyquist frequency
    st.pyplot(fig)

#play selected sample
def play_sample(selected_file):
    y, sr = lib.load(selected_file)
    duration = len(y)/sr
    st.subheader("Play sample")
    st.write(f"Duration: {duration:.2f} seconds")
    st.audio(selected_file)

#load favorite files
def load_favorite_files():
    if os.path.exists("favorites.json"):
        with open("favorites.json", "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

#checkoff a fav sample
def toggle_fav_sample(selected_file, favorites):
    is_fav = favorites.get(selected_file, False)
    new_fav = st.checkbox("Favorite ⭐", value=is_fav)
    favorites[selected_file] = new_fav
    fav_dir = "Favorites"
    os.makedirs(fav_dir, exist_ok=True)
    dest_path = os.path.join(fav_dir, os.path.basename(selected_file))

    if new_fav:
        if not os.path.exists(dest_path):
            try:
                shutil.copy(selected_file, dest_path)
                st.success("Added to Favorites folder!")
            except Exception as e:
                st.error(f"Failed to copy to Favorites: {e}")
    else:
        if os.path.exists(dest_path):
            os.remove(dest_path)
            st.info("Removed from Favorites folder")
    
    with st.sidebar:
        st.subheader("⭐ Favorites")
        fav_dir = "Favorites"
        if os.path.exists(fav_dir):
            fav_samples = [f for f in os.listdir(fav_dir) if f.endswith(('.wav', '.mp3', '.flac'))]
            if fav_samples:
                chosen = st.selectbox("Play a favorite:", fav_samples)
                st.audio(os.path.join(fav_dir, chosen))
            else:
                st.write("No favorites yet.")

    return favorites

#save favorite files
def save_favorites(favorites):
    with open("favorites.json", "w") as f:
        json.dump(favorites, f, indent=2)

#load renamed current file
def load_renamed_files():
    if os.path.exists("renamed.json"):
        with open("renamed.json", "r") as r:
            try:
                return json.load(r)
            except json.JSONDecodeError:
                return {}
    return {}

#change name input
def change_file_name(selected_file, renamed_files):
    existing_name = renamed_files.get(selected_file, os.path.splitext(os.path.basename(selected_file))[0])
    if not isinstance(existing_name, str):
        existing_name = str(existing_name)
    new_renamed = st.text_input("Rename sample: " ,value=existing_name)
    if isinstance(new_renamed, str) and new_renamed.strip() != "":
        renamed_files[selected_file] = new_renamed.strip()
    renamed_files[selected_file] = new_renamed
    return renamed_files

#save renamed files
def save_renamed(renamed_files):
    with open("renamed.json", "w") as r:
        json.dump(renamed_files, r, indent=2)

BASE_SAVE_DIR = "RenamedSamples"

#save edited file as:
def save_edited_as(selected_file, rename, output_destination):
    rename = str(rename).strip()
    output_destination = str(output_destination).strip()
    rename = sanitize_filename(rename)

    if not rename.endswith(".wav"):
        rename += ".wav"

    folder_path = os.path.join("RenamedSamples", output_destination)
    os.makedirs(folder_path, exist_ok=True)
    save_path = os.path.join(folder_path, rename)

    try:
        # Load audio and fix stereo shape
        y, sr = lib.load(selected_file, sr=None, mono=False)
        if isinstance(y, np.ndarray) and y.ndim == 2 and y.shape[0] == 2:
            y = y.T

        # Confirm write path
        print("Attempting to save:", save_path)
        sf.write(save_path, y, sr, format="WAV", subtype="PCM_16")

    except Exception as e:
        st.error(f"⚠️ Failed to save: Error opening `{save_path}`: {e}")
        return None

    return save_path

def sanitize_filename(name):
    import re
    name = str(name)
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip()
    if name.lower() in ["con", "prn", "aux", "nul", "true", "false"]:
        name = f"sample_{name}"
    return name

#pitching samples up and down
def pitch_sample(file_path, semitones,bit_depth = 'PCM_32'):
    y, sr = lib.load(file_path, sr=None, mono=True)
    y_shifted = lib.effects.pitch_shift(y, sr=sr, n_steps=semitones)

    delay_ms = 7 
    delay_samples = int(sr * delay_ms / 1000)

    left = y_shifted
    right = np.pad(y_shifted, (delay_samples, 0))[:len(y_shifted)]

    y_stereo = np.column_stack((left, right)).astype(np.float32)

    buffer = io.BytesIO()
    sf.write(buffer, y_stereo, sr, format='WAV', subtype=bit_depth)
    buffer.seek(0)
    return buffer

def save_buffer_to_wav(buffer, filename, folder):
    os.makedirs(folder, exist_ok=True)

    filename = sanitize_filename(filename)
    if not filename.endswith(".wav"):
        filename += ".wav"

    save_path = os.path.join(folder, filename)

    buffer.seek(0)

    try:
        with open(save_path, "wb") as f:
            f.write(buffer.read())
    except Exception as e:
        st.error(f"⚠️ Failed to save: {e}")
        return None

    return save_path

#main title       
st.title("Sample Wizard")

#getting the folder path
folder_path = get_folder_path()

#logic main 
if folder_path and os.path.exists(folder_path):
    
    favorites = load_favorite_files()
    renamed_files = load_renamed_files()
    audio_files = scan_for_audio_files(folder_path)
    sorted_files = sort_supported_audio_files(audio_files)

    selected_file = selected_from_sorted_sample_list(sorted_files)

    if selected_file:
        favorites = toggle_fav_sample(selected_file, favorites)

    rename = renamed_files.get(
    selected_file, os.path.splitext(os.path.basename(selected_file))[0]
    )

    if not isinstance(rename, str):
        rename = str(rename)

    rename = sanitize_filename(rename.strip())

    with st.sidebar:
        st.subheader("📂 Custom Folders (Renamed Samples)")

        if os.path.exists(BASE_SAVE_DIR):
            custom_folders = [f for f in os.listdir(BASE_SAVE_DIR) 
                            if os.path.isdir(os.path.join(BASE_SAVE_DIR, f))]

            if custom_folders:
                chosen_folder = st.selectbox("Select a folder", custom_folders)
                folder_path = os.path.join(BASE_SAVE_DIR, chosen_folder)

                sample_files = scan_for_audio_files(folder_path)
                st.markdown(f"**Samples in `{chosen_folder}`:**")
                for s in sample_files:
                    st.write(os.path.basename(s))
                    st.audio(s)
            else:
                st.write("No custom folders yet.")
        else:
            st.info("No renamed samples saved yet.")

    save_favorites(favorites)
    save_renamed(renamed_files)

    play_sample(selected_file)
    if selected_file:
        renamed_files = change_file_name(selected_file, renamed_files)
    
    original = os.path.basename(selected_file)
    edited = rename
    output_destination = st.text_input("Custom folder name for edited samples:")
    if st.button("💾 Save As"):
        if output_destination == "" :
            st.error("Please enter customer folder name")
        else:
            if edited == original or edited == "":
                st.error("Please make changes to save as different file!")
            else:
                save_path = save_edited_as(selected_file, edited, output_destination)
                if save_path:
                    st.success(f"Saved to: {save_path}")    

    semitones = st.slider("Pitch shift (in semitones)", -12,12,0)
    if selected_file and semitones != 0:
        bit_depth = st.selectbox("Select bit depth", ["PCM_16", "PCM_24", "PCM_32", "FLOAT"])
        pitched_audio = pitch_sample(selected_file, semitones, bit_depth)
        st.audio(pitched_audio, format='audio/wav')
    
    if semitones != 0 and selected_file:
        st.markdown("### 🎵 Save Pitched Sample")

        pitch_rename = st.text_input("Rename pitched sample:")
        pitch_output_folder = st.text_input("Folder for pitched sample:", value="PitchedSamples")

        if st.button("💾 Save Pitched Sample"):
            if pitch_rename.strip() == "" or pitch_rename.strip() == os.path.basename(selected_file):
                st.error("Please enter a unique name for the pitched sample.")
            else:
                save_path = save_buffer_to_wav(
                    pitched_audio,
                    pitch_rename,
                    os.path.join("RenamedSamples", pitch_output_folder)
                )
                if save_path:
                    st.success(f"Pitched sample saved to: {save_path}")

    display_waveform(selected_file)
    spectrum_analysis(selected_file)
else:
    st.info("Please enter a valid folder path.")
    
