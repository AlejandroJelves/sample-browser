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
    st.subheader("Waveform")
    y, sr = lib.load(selected_file)
    fig, ax = plt.subplots()
    ax.plot(y)
    ax.set_title("Sample Waveform")
    st.pyplot(fig)

#note detection
def spectrum_analysis(selected_file):
    st.subheader("Spectrum Analysis")
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
    if os.path.exists("sample.data.json"):
        with open("sample.data.json", "r") as f:
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
    return favorites

#save favorite files
def save_favorites(favorites):
    with open("sample.data.json", "w") as f:
        json.dump(favorites, f, indent= 2)

#load renamed current file
def load_renamed_files():
    if os.path.exists("sample.data.json"):
        with open("sample.data.json", "r") as r:
            try:
                return json.load(r)
            except json.JSONDecodeError:
                return {}
    return {}

#change name input
def change_file_name(selected_file, renamed_files):
    existing_name = renamed_files.get(selected_file, os.path.splitext(os.path.basename(selected_file))[0])
    new_renamed = st.text_input("Rename sample: " ,value=existing_name)
    renamed_files[selected_file] = new_renamed
    return renamed_files

#save renamed files
def save_renamed(renamed_files):
    with open("sample.data.jsn", "w") as r:
        json.dump(renamed_files, r , indent=2)

#save edited file as:
def save_edited_as(selected_file, rename, output_destination):
    os.makedirs(output_destination, exist_ok=True)
    y, sr = lib.load(selected_file)
    if not rename.endswith(".wav"):
        rename+= ".wav"
    save_path = os.path.join(output_destination, rename)
    sf.write(save_path, y, sr )
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
        renamed_files = change_file_name(selected_file, renamed_files)
    
    rename = renamed_files.get(
    selected_file,
    os.path.splitext(os.path.basename(selected_file))[0]
    )
    
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


    save_favorites(favorites)
    save_renamed(renamed_files)


    play_sample(selected_file)

    display_waveform(selected_file)
    spectrum_analysis(selected_file)
else:
    st.info("Please enter a valid folder path.")
    
