import streamlit as st
import requests

# Title of the app
st.title("Video Upload and Display App")

# Upload video file
video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if st.button('Create video'):
    if video_file is not None:
        # URL của server Flask trên Google Colab
        colab_url = "http://4789-34-19-110-150.ngrok-free.app/run_model"  # Thay thế bằng URL ngrok của bạn

        # Gửi yêu cầu POST với tệp video
        files = {'video_file': video_file.getvalue()}
        response = requests.post(colab_url, files=files)

        if response.status_code == 200:
            st.success("Model execution initiated!")

            # Lấy đường dẫn video kết quả từ phản hồi
            result_video_path = response.json().get('result_video_path')

            # URL để tải video từ Google Colab
            video_url = f"http://4789-34-19-110-150.ngrok-free.app/get_video/{result_video_path}"  # Thay thế bằng URL ngrok của bạn

            # Hiển thị video kết quả
            st.video(video_url)
        else:
            st.error("Failed to initiate model execution")
    else:
        st.error("Please upload a video file before creating video.")
