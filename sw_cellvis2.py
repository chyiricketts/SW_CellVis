import os
import time
from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use("Agg")  # Use a non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from PIL import Image

app = Flask(__name__)

def generate_image(title_text, color_mode, overlay_mask, axis_toggle):
    """Generate an image with optional mask overlay"""
    img_path = os.path.join("static", "uploads", "pro-siNC.bmp")
    img = Image.open(img_path)
    img = np.array(img)

    if color_mode == "Greyscale":
        img = np.mean(img, axis=2)  # Convert to grayscale

    fig, ax = plt.subplots()
    ax.imshow(img, cmap="gray" if color_mode == "Greyscale" else None)

    print("check")
    if title_text:
        ax.set_title(title_text)
        print(f"Title set: {title_text}")  # Debugging check


    # Overlay mask if enabled
    if overlay_mask:
        mask = np.zeros((50, 50))
        mask[50//4:3*50//4, 50//4:3*50//4] = 1  # Example square mask
        ax.imshow(mask, cmap="Reds", alpha=0.5)  # Red semi-transparent overlay

    if axis_toggle: 
        ax.axis("on")
    else:
        ax.axis("off")

    save_path = os.path.join("static", "figures", "w_generated_image.png")
    plt.savefig(save_path, format="png", bbox_inches="tight")
    plt.close(fig)
    
    return img_path


@app.route("/update_graph", methods=["POST"])
def update_graph():
    data = request.json
    print(f"Received data: {data}")  # Debugging check
    title_text = data.get("title_text", "")
    color_mode = data.get("color_mode", "Original")
    overlay_mask = data.get("overlay_mask", False)
    axis_toggle = data.get("axis_toggle", False)

    save_path = os.path.join("static", "figures", "w_generated_image.png")

    generate_image(title_text, color_mode, overlay_mask, axis_toggle)
    return jsonify({"img": f"{save_path}?t={int(time.time())}"})  # Add timestamp to prevent caching


@app.route("/open_wholeimage")
def open_wholeimage():
    generate_image("", "Original", False, False)  # Ensure image is generated
    return render_template("wholeimage2.html", image_path="/static/figures/w_generated_image.png")




@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
