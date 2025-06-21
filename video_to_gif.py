import streamlit as st
import subprocess
import os
import tempfile
from pathlib import Path


st.set_page_config(page_title="Video to GIF Converter", layout="centered")
st.title("🎬 Video to GIF Converter")
st.markdown("Upload an MP4 or WebM video, set your options, and download a smooth animated GIF!")

# Upload video
video_file = st.file_uploader("Upload video", type=["mp4"])

# Settings
fps = st.slider("Frames per second (FPS)", min_value=1, max_value=30, value=10)
width = st.slider("GIF width (px)", min_value=100, max_value=1080, value=480)

if video_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_ext = Path(video_file.name).suffix
        input_path = os.path.join(tmpdir, f"input{input_ext}")
        palette_path = os.path.join(tmpdir, "palette.png")
        output_path = os.path.join(tmpdir, "output.gif")

        # Save uploaded video to temp file
        with open(input_path, "wb") as f:
            f.write(video_file.read())

        st.info("🔄 Converting... Please wait.")

        # 1. Generate palette
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,palettegen",
            palette_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 2. Generate GIF using palette
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-i", palette_path,
            "-filter_complex", f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse",
            output_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        st.success("✅ Conversion complete!")

        # Preview and download
        with open(output_path, "rb") as f:
            gif_bytes = f.read()
            st.image(gif_bytes, caption="🎞️ Preview of your GIF", use_column_width=True)
            st.download_button("⬇️ Download GIF", gif_bytes, "output.gif", "image/gif")
