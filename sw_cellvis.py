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
from skimage import measure
from PIL import ImageEnhance


app = Flask(__name__)

def generate_image(title_text, color_mode, overlay_mask, axis_toggle, mask_border, brightness_adjust):
    """Generate an image with optional mask overlay"""
    img_path = os.path.join("static", "uploads", "pro-siNC.bmp")
    npy_file = os.path.join("static", "uploads", "pro-siNC_seg.npy")

    img = Image.open(img_path)
    img = np.array(img)

    mask_data = np.load(npy_file, allow_pickle=True).item()
    masks = mask_data['masks']
    masks_cells = np.ma.masked_where(masks == 0, masks)
    cell_labels = np.unique(masks)
    cell_labels = cell_labels[cell_labels > 0]  # remove background (0)

    fig, ax = plt.subplots()
    
    img_pil = Image.fromarray(img)  # Convert the NumPy array to a PIL Image object
    enhancer = ImageEnhance.Brightness(img_pil)  # Use the PIL Image for brightness enhancement
    brightness_adjust = float(brightness_adjust)
    img_pil = enhancer.enhance(brightness_adjust)  # Adjust brightness

    # Convert back to NumPy array if necessary for further processing
    img = np.array(img_pil)


    if color_mode == "Greyscale":
        img = np.mean(img, axis=2)  # Convert to grayscale


    ax.imshow(img, cmap="gray" if color_mode == "Greyscale" else None)

    print("check")
    if title_text:
        ax.set_title(title_text)
        print(f"Title set: {title_text}")  # Debugging check


    # Overlay mask if enabled
    if overlay_mask:
        ax.imshow(masks_cells, cmap = "Reds", alpha = 0.5)  # Use a colormap to differentiate masks

    if axis_toggle: 
        ax.axis("on")
    else:
        ax.axis("off")

    # Mask Borders, first needs cell_labels defined
    if mask_border:
        for label in cell_labels:
            contours = measure.find_contours(masks == label, level = 0.5)
            print(f"Label {label}: {len(contours)} contours found")  # Debugging line
            for contour in contours:
                y_coords, x_coords = contour[:, 0], contour[:, 1]
                ax.plot(x_coords, y_coords, color='red', linewidth=0.5)  # Fixed border plotting
                #plt.scatter(x_coords, y_coords, s=1, color='red')

    save_path = os.path.join("static", "figures", "w_generated_image.png")
    plt.savefig(save_path, format="png", bbox_inches="tight")
    #plt.close(fig)
    
    return img_path


@app.route("/update_graph", methods=["POST"])
def update_graph():
    data = request.json
    print(f"Received data: {data}")  # Debugging check
    title_text = data.get("title_text", "")
    color_mode = data.get("color_mode", "Original")
    overlay_mask = data.get("overlay_mask", False)
    axis_toggle = data.get("axis_toggle", False)
    mask_border = data.get("mask_border", False)
    brightness_adjust = data.get("brightness_adjust", 1)

    save_path = os.path.join("static", "figures", "w_generated_image.png")

    generate_image(title_text, color_mode, overlay_mask, axis_toggle, mask_border, brightness_adjust)
    return jsonify({"img": f"{save_path}?t={int(time.time())}"})  # Add timestamp to prevent caching


@app.route("/open_wholeimage")
def open_wholeimage():
    generate_image("", "Original", False, False, False, 1)  # Ensure image is generated
    return render_template("wholeimage.html", image_path="/static/figures/w_generated_image.png")

@app.route("/open_blip")
def open_blip():
    return render_template("blip.html")

@app.route("/open_biogpt")
def open_biogpt():
    return render_template("biogpt.html")



@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
