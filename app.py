import streamlit as st
import os
import librosa as lib
import matplotlib.pyplot as plt

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
        return selected_file
    return None

#display wavform
def display_waveform(selected_file):
    y, sr = lib.load(selected_file)
    fig, ax = plt.subplots()
    ax.plot(y)
    ax.set_title("Sample Waveform")
    st.pyplot(fig)
  
    
#play selected sample
def play_sample(selected_file):
    st.subheader("Play sample")
    st.audio(selected_file)

#main title       
st.title("Sample Wizard")

#getting the folder path
folder_path = get_folder_path()

#logic for scanning and displaying audio files
if folder_path and os.path.exists(folder_path):
    audio_files = scan_for_audio_files(folder_path)
    sorted_files = sort_supported_audio_files(audio_files)

    selected_file = selected_from_sorted_sample_list(sorted_files)
    display_waveform(selected_file)
    play_sample(selected_file)


else:
    st.info("Please enter a valid folder path.")
    
