import os
import time
from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from PIL import Image

app = Flask(__name__)

def generate_image(title_text, color_mode, overlay_mask):
    """Generate an image with optional mask overlay"""
    img_path = os.path.join("static", "uploads", "pro-siNC.bmp")
    img = Image.open(img_path)
    img = np.array(img)

    if color_mode == "Greyscale":
        img = np.mean(img, axis=2)  # Convert to grayscale

    fig, ax = plt.subplots()
    ax.imshow(img, cmap="gray" if color_mode == "Greyscale" else None)

    if title_text:
        ax.set_title(title_text)

    # Overlay mask if enabled
    if overlay_mask:
        mask = np.zeros((50, 50))
        mask[50//4:3*50//4, 50//4:3*50//4] = 1  # Example square mask
        ax.imshow(mask, cmap="Reds", alpha=0.5)  # Red semi-transparent overlay

    ax.axis("off")

    save_path = os.path.join("static", "figures", "w_generated_image.png")
    buf = io.BytesIO()
    #plt.savefig(buf, format="png", bbox_inches="tight")
    plt.savefig(save_path, format="png", bbox_inches="tight")
    plt.close(fig)
    #buf.seek(0)
    
    #img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_path


@app.route("/update_graph", methods=["POST"])
def update_graph():
    data = request.json
    title_text = data.get("title_text", "")
    color_mode = data.get("color_mode", "Original")
    overlay_mask = data.get("overlay_mask", False)

    save_path = os.path.join("static", "figures", "w_generated_image.png")

    #img_base64 = generate_image(title_text, color_mode, overlay_mask)
    #return jsonify({"image": f"data:image/png;base64,{img_base64}"})
    #return jsonify({"img": f"/{save_path}"})
    return jsonify({"img": f"{save_path}?t={int(time.time())}"})  # Add timestamp to prevent caching


@app.route("/open_wholeimage")
def open_wholeimage():
    img_base64 = generate_image("", "Original", False)
    return render_template("wholeimage2.html", image_data=f"data:image/png;base64,{img_base64}")



@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
