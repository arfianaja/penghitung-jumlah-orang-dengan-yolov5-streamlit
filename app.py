from multiprocessing.sharedctypes import Value
from pickle import FALSE
from tracemalloc import stop
from track import *
import tempfile
import cv2
import torch
import streamlit as st
from datetime import datetime
import os
from PIL import Image
import base64

count_results = []
# Initialize up_count and down_count
up_count = 0
down_count = 0


def beranda():
    logo_path = os.path.join('images', 'logo.png')
    logo_image = Image.open(logo_path)
    
    # Resize the logo to the desired dimensions (e.g., 200x200 pixels)
    resized_logo = logo_image.resize((200, 200))
    set_background('images/bg1.jpg')
    st.markdown(
        f"""
        <div style='display: flex; justify-content: center;'>
            <img src='data:image/png;base64,{image_to_base64(resized_logo)}' alt='logo' style='width:200px; height:200px; object-fit: contain;'>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style='display: flex; justify-content: center;'>
            <h2 style='color: black;'>Perancangan Sistem Penghitungan Jumlah Keluar Masuk Orang Di Pelabuhan Klademak</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def image_to_base64(image):
    from io import BytesIO
    import base64

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    footer {
        visibility: hidden;
    }
    footer:after {
        content: 'gasasa';
        visibility: visible;
        display: block;
        position: relative;
        #background-color: red;
        padding: 5px;
        top: 2px;
    }
    #MainMenu{
        visibility:hidden;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
def deteksi():
    st.title('Aplikasi Deteksi & Penghitungan Pengunjung')
    st.markdown('<h3 style="color: red"> with Yolov5 </h3', unsafe_allow_html=True)

    # upload video
    video_file_buffer = st.sidebar.file_uploader("Upload a video", type=['mp4', 'mov', 'avi'])
    use_webcam = st.sidebar.checkbox('Gunakan Webcam')

    if use_webcam:
        st.sidebar.text('Input video: Webcam')
    elif video_file_buffer:
        st.sidebar.text('Input video')
        st.sidebar.video(video_file_buffer)
        # save video from streamlit into "videos" folder for future detect
        with open(os.path.join('videos', video_file_buffer.name), 'wb') as f:
            f.write(video_file_buffer.getbuffer())

    st.sidebar.markdown('---')
    st.sidebar.title('Settings')
    # custom class
    show_custom_class = False  # Langsung set ke False untuk menyembunyikan opsi
    custom_class = False
    assigned_class_id = [0, 1, 2, 3]
    names = ['person', 'orang']

    if custom_class:
        assigned_class_id = []
        assigned_class = st.sidebar.multiselect('Select custom classes', list(names), default=["person", "orang"])

        for each in assigned_class:
            assigned_class_id.append(names.index(each))

    status = st.empty()
    stframe = st.empty()
    if video_file_buffer is None:
        status.markdown('<font size= "4"> **Status:** Waiting for input </font>', unsafe_allow_html=True)
    else:
        status.markdown('<font size= "4"> **Status:** Ready </font>', unsafe_allow_html=True)

    person1, person2,  _, _ = st.columns(4)
    with person1:
        st.markdown('**Keluar**')
        person_text = st.markdown('__')
    
    with person2:
        st.markdown('**Masuk**')
        person2_text = st.markdown('__')
    
    fps, _,  _, _  = st.columns(4)
    with fps:
        st.markdown('**FPS**')
        fps_text = st.markdown('__')

    track_button = st.sidebar.button('START')
    if track_button:
        # reset ID and count from 0
        up_count = 0  # Add this line to reset up_count
        down_count = 0  # Add this line to reset down_count

        opt = parse_opt()
        opt.source = '0' if use_webcam else f'videos/{video_file_buffer.name}'

        status.markdown('<font size= "4"> **Status:** Running... </font>', unsafe_allow_html=True)

        with torch.no_grad():
            detect(opt, stframe, person_text, person2_text, fps_text, assigned_class_id)
        status.markdown('<font size= "4"> **Status:** Finished ! </font>', unsafe_allow_html=True)

# Fungsi Utama
def utama():
    # Navigasi di Sidebar
    halaman = {
        'Beranda': beranda,
        'Deteksi': deteksi
    }

    st.sidebar.title('Navigasi')
    pilihan = st.sidebar.selectbox('Pergi ke', list(halaman.keys()))

    # Jalankan halaman yang dipilih
    halaman[pilihan]()

    
if __name__ == '__main__':
    utama()

