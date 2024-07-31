import streamlit as st
import av
import os
from PIL import Image
import subprocess
import time
import requests


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
# detector = st.radio("Choose an option:", ["yolo", "maskrcnn"],index=0,horizontal=True)
# if tracking_method=='pose':
#     run_smplify = st.checkbox("Chạy SMPLify", value=True)
# sideview = st.checkbox("Góc nhìn thay thế", value=False)
# smooth = st.checkbox("Làm mượt", value=False)

if st.button('Create video'):
    if video_file is not None:
        # URL của server Flask trên Google Colab
        colab_url = "https://18e2-35-243-176-77.ngrok-free.app/run_model"  # Thay thế bằng URL ngrok của bạn

        # Gửi yêu cầu POST với tệp video
        files = {'video_file': video_file.getvalue()}
        response = requests.post(colab_url, files=files)

        if response.status_code == 200:
            st.success("Model execution initiated!")

            # Lấy đường dẫn video kết quả từ phản hồi
            result_video_path = response.json().get('result_video_path')

            # URL để tải video từ Google Colab
            video_url = f"https://18e2-35-243-176-77.ngrok-free.app/get_video/{result_video_path}"  # Thay thế bằng URL ngrok của bạn

            # Hiển thị video kết quả
            st.video(video_url)
        else:
            st.error("Failed to initiate model execution")
    else:
        st.error("Please upload a video file before creating video.")
