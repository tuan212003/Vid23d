import streamlit as st
import av
import os
from PIL import Image
import subprocess
import time

# Title of the app
st.title("Video Upload and Display App")

# Upload video file
video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
file_name=''
# If a video file is uploaded
if video_file is not None:
    # Display the video
    st.video(video_file)
    file_name = video_file.name

VideoFolder=st.text_input('Nhập file_output:')
VideoPath = VideoFolder + file_name 
 
# tracking_method = st.radio("Choose an option:", ["bbox", "pose"],index=0,horizontal=True)
detector = st.radio("Choose an option:", ["yolo", "maskrcnn"],index=0,horizontal=True)
# if tracking_method=='pose':
#     run_smplify = st.checkbox("Chạy SMPLify", value=True)
sideview = st.checkbox("Góc nhìn thay thế", value=False)
smooth = st.checkbox("Làm mượt", value=False)

if st.button('Creat video'):
    # Chạy lệnh python demo.py với các tham số
    process = subprocess.Popen(['python', 'demo.py', '--vid_file', VideoPath , '--output_folder', VideoFolder])

    name = os.path.splitext(file_name)[0]
    video_output=VideoFolder+name+'/'+ name + '_vibe_result.mp4'
    st.video(video_output)
