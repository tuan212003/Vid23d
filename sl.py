import streamlit as st
from demo import main

st.title("Video to 3D")

uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])
st.video(uploaded_video)

if uploaded_video is not None:
    # Lưu video vào hệ thống tập tin của Colab
    with open('/content/Vid23d/ResultFolder/video.mp4', 'wb') as f:
        f.write(uploaded_video.getbuffer())
    st.success("Video đã lưu thành công!")

class Args:
    vid_file = ''
    output_folder = ''
    tracking_method = 'bbox'
    detector = 'yolo'
    yolo_img_size = 416
    tracker_batch_size = 12
    staf_dir = '/home/mkocabas/developments/openposetrack'
    vibe_batch_size = 450
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
args.vid_file='/content/Vid23d/ResultFolder/video.mp4'
args.output_folder='/content/Vid23d/ResultFolder/'

if st.button("Tạo video 3d"):
    main(args)
    video_output_path='/content/Vid23d/ResultFolder/video/video_vibe_result.mp4'
    st.video(video_output_path)

