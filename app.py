import streamlit as st
import os

#take in valid folder intput
def get_folder_path():
    folder_path = st.text_input("Enter the folder path for desired samples!")
    if os.path.exists(folder_path):
        st.success("Folder path is valid!")
            
    else:
        st.error("Folder path is not valid!")
    return folder_path
            
#scan for supported audio sample files
def scan_for_audio_files(folder_path):
    supported_formats = ('.wav', '.mp3', '.flac')
    audio_files = []
    for root, dirs, files in os.walk(folder_path):
        for item in files:
            if item.endwith(supported_formats):
                audio_files.append(os.path.join(root , item))
            else:
                st.error(f"File {item} is not a supported audio format.")
    return audio_files

#sort the audio files
def sort_supported_audio_files(audio_files):
    sorted_files = sorted(audio_files)
    return sorted_files

def display_supported_audio_files(sorted_files):
    st.markdown("### Supported Audio Files")
    for file in sorted_files:
        st.write(file)
        
st.title("Sample Wizard")

folder_path = get_folder_path()

if folder_path and os.path.exists(folder_path):
    audio_files = scan_for_audio_files(folder_path)
    sorted_files = sort_supported_audio_files(audio_files)
    display_supported_audio_files(sorted_files)
else:
    st.info("Please enter a valid folder path.")
    
