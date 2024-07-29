import streamlit as st
import av
import os
from PIL import Image
from demo import main


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
VideoFolder='/content/Vid23d/ResultFolder/'
VideoPath = VideoFolder + file_name  
tracking_method = st.radio("Choose an option:", ["bbox", "pose"],index=0,horizontal=True)
detector = st.radio("Choose an option:", ["yolo", "maskrcnn"],index=0,horizontal=True)
if tracking_method=='pose':
    run_smplify = st.checkbox("Chạy SMPLify", value=True)
sideview = st.checkbox("Góc nhìn thay thế", value=False)
smooth = st.checkbox("Làm mượt", value=False)

class Args:
    vid_file = ''
    output_folder = ''
    tracking_method = '' 
    detector = '' 
    yolo_img_size = 416
    tracker_batch_size = 12
    staf_dir = '/home/mkocabas/developments/openposetrack'
    vibe_batch_size = 460
    display = False
    run_smplify = False
    no_render = False
    wireframe = False
    sideview = False
    save_obj = False
    smooth = False
    smooth_min_cutoff = 0.004
    smooth_beta = 0.7

args=Args()
args.vid_file=VideoPath
args.output_folder=VideoFolder
args.tracking_method=tracking_method
args.detector=detector
args.run_smplify=run_smplify
args.sideview=sideview
args.smooth=smooth

st.button('Creat video')
if st.button("Click me"):
    main(args)

name = os.path.splitext(file_name)[0]
video_output=VideoFolder+name+'/'+ name + '_vibe_result.mp4'
st.video(video_output)
