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

def generate_image(title_text, color_mode, overlay_mask, axis_toggle, mask_border, brightness_adjust, overlay_adjust, border_linewidth, mask_labels, image_choice1, image_choice2, image_choice3):
    """Generate an image with optional mask overlay"""
    print("imagechoice: ")
    print(image_choice1, image_choice2, image_choice3)

    if image_choice1 == True:
        image_choice = 0
    elif image_choice2 == True:
        image_choice = 1
    elif image_choice3 == True:
        image_choice = 2

    img_paths = [os.path.join("static", "uploads", "D04F24Composite.bmp"),
                 os.path.join("static", "uploads", "E10F5Composite.bmp"),
                 os.path.join("static", "uploads", "F09F38Composite.bmp")]

    npy_paths = [os.path.join("static", "uploads", "D04F24Composite_seg.npy"),
                 os.path.join("static", "uploads", "E10F5Composite_seg.npy"),
                 os.path.join("static", "uploads", "F09F38Composite_seg.npy")]

    img_path = img_paths[image_choice]
    npy_file = npy_paths[image_choice]

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

    if title_text:
        ax.set_title(title_text)
        print(f"Title set: {title_text}")  # Debugging check

    overlay_adjust = float(overlay_adjust)

    # Overlay mask if enabled
    if overlay_mask:
        ax.imshow(masks_cells, cmap = "Reds", alpha = overlay_adjust)  # Use a colormap to differentiate masks

    if axis_toggle: 
        ax.axis("on")
    else:
        ax.axis("off")

    border_linewidth = float(border_linewidth)

    # Mask Borders, first needs cell_labels defined
    if mask_border:
        for label in cell_labels:
            contours = measure.find_contours(masks == label, level = 0.5)
            print(f"Label {label}: {len(contours)} contours found")  # Debugging line
            for contour in contours:
                y_coords, x_coords = contour[:, 0], contour[:, 1]
                ax.plot(x_coords, y_coords, color='red', linewidth=border_linewidth)  # Fixed border plotting
                #plt.scatter(x_coords, y_coords, s=1, color='red')

    # Mask Labels
    if mask_labels: 
         for label in cell_labels:
                mask_coords = np.argwhere(masks == label)  # Get pixel coordinates of the mask
                if mask_coords.size > 0:
                    centroid = np.mean(mask_coords, axis=0)  # Compute centroid
                    plt.text(centroid[1], centroid[0], str(label), 
                             color="Red", fontsize=10, fontweight='bold', ha='center', va='center')

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
    overlay_adjust = data.get("overlay_adjust", 0.5)
    border_linewidth = data.get("border_linewidth", 1)
    mask_labels = data.get("mask_labels", False)
    image_choice1 = data.get("image_choice1", True)
    image_choice2 = data.get("image_choice2", False)
    image_choice3 = data.get("image_choice3", False)

    save_path = os.path.join("static", "figures", "w_generated_image.png")

    generate_image(title_text, color_mode, overlay_mask, axis_toggle, mask_border, brightness_adjust, overlay_adjust, border_linewidth, mask_labels, image_choice1, image_choice2, image_choice3)
    return jsonify({"img": f"{save_path}?t={int(time.time())}"})  # Add timestamp to prevent caching


@app.route("/open_wholeimage")
def open_wholeimage():
    generate_image("", "Original", False, False, False, 1, 0.5, 1, False, True, False, False)  # Ensure image is generated
    return render_template("wholeimage.html", image_path="/static/figures/w_generated_image.png")

@app.route("/open_featureex")
def open_featureex():
    return render_template("featureex.html")

@app.route("/open_blip")
def open_blip():
    return render_template("blip.html")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
