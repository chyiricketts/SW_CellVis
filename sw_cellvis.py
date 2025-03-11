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
from scipy.spatial.distance import pdist


app = Flask(__name__)

def choose_image(image_choice1, image_choice2, image_choice3):
    img_paths = [os.path.join("static", "uploads", "D04F24Composite.bmp"),
                 os.path.join("static", "uploads", "E10F5Composite.bmp"),
                 os.path.join("static", "uploads", "F09F38Composite.bmp")]

    npy_paths = [os.path.join("static", "uploads", "D04F24Composite_seg.npy"),
                 os.path.join("static", "uploads", "E10F5Composite_seg.npy"),
                 os.path.join("static", "uploads", "F09F38Composite_seg.npy")]
    
    if image_choice1 == True:
        image_choice = 0
    elif image_choice2 == True:
        image_choice = 1
    elif image_choice3 == True:
        image_choice = 2
    else:
        image_choice = 0

    return (img_paths[image_choice], npy_paths[image_choice])



def generate_image(title_text, color_mode, overlay_mask, axis_toggle, mask_border, brightness_adjust, overlay_adjust, border_linewidth, mask_labels, image_choice1, image_choice2, image_choice3):
    """Generate an image with optional mask overlay"""

    img_path, npy_file = choose_image(image_choice1, image_choice2, image_choice3)

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



def compile_feature_data(image_choice1, image_choice2, image_choice3, show_average, show_individual, show_sizes, show_cellcenters, show_intensity, color_mode):
    
    output = ""

    img_path, npy_file = choose_image(image_choice1, image_choice2, image_choice3)

    img = Image.open(img_path)
    img = np.array(img)

    mask_data = np.load(npy_file, allow_pickle=True).item()
    masks = mask_data['masks']
    masks_cells = np.ma.masked_where(masks == 0, masks)
    cell_labels = np.unique(masks)
    cell_labels = cell_labels[cell_labels > 0]  # remove background (0)

    # Total Pixels
    unique_labels, counts = np.unique(masks, return_counts=True)
    pixel_counts = {label: count for label, count in zip(unique_labels, counts) if label != 0}
    mean_pixel_counts = np.mean(list(pixel_counts.values()))
    mean_pixel_counts = round(mean_pixel_counts, 4)

    # Cell Centers
    cell_centers = {}
    for label in cell_labels:
        cell_coords = np.column_stack(np.where(masks == label))  # (row, col) positions
        r_min, c_min = cell_coords.min(axis=0)
        r_max, c_max = cell_coords.max(axis=0)
        center_r, center_c = int((r_min + r_max) // 2), int((c_min + c_max) // 2)  # Convert to int
        cell_centers[label] = (center_r, center_c)
    mean_x = np.mean([center[0] for center in cell_centers.values()])
    mean_y = np.mean([center[1] for center in cell_centers.values()])
    mean_x = round(mean_x, 4)
    mean_y = round(mean_y, 4)

    # Mean Intensity
    img_check = Image.open(img_path)
    if img_check.mode != "L":  # "L" mode in PIL means grayscale
        image_gray_version = img_check.convert("L")
    img_gray = np.array(image_gray_version)

    cell_intensities = {}
    for label in unique_labels:
        cell_pixels = img_gray[masks == label]
        mean_intensity = np.mean(cell_pixels)
        cell_intensities[label] = round(mean_intensity, 4)
    mean_cell_intensity = np.mean(list(cell_intensities.values()))
    mean_cell_intensity = round(mean_cell_intensity, 4)

    # Intensity channels
    image = Image.open(img_path).convert("RGB")
    img_rgb = np.array(image)

    red_channel = img_rgb[:, :, 0]
    green_channel = img_rgb[:, :, 1]
    blue_channel = img_rgb[:, :, 2]

    mean_red_intensity = round(np.mean(red_channel), 4)
    mean_green_intensity = round(np.mean(green_channel), 4)
    mean_blue_intensity = round(np.mean(blue_channel), 4)

    cell_rgb_intensities = {}
    for label in cell_labels:
        mask = (masks == label)
        
        red_intensity = np.mean(red_channel[mask])
        green_intensity = np.mean(green_channel[mask])
        blue_intensity = np.mean(blue_channel[mask])

        cell_rgb_intensities[label] = {
            "Red": round(red_intensity, 4),
            "Green": round(green_intensity, 4),
            "Blue": round(blue_intensity, 4)
        }

    if show_sizes: 
        output += ("<b>Cell Sizes </b><br>")
        if show_average:
            output += (f"<b>Average: </b> {mean_pixel_counts}<br>")
        if show_individual:
            for mask in cell_labels:
                output += (f"Mask {mask}: {pixel_counts[mask]}<br>")
            output += ("<br>")
    
    if show_cellcenters:
        output += ("<b>Cell Centers </b><br>")
        if show_average:
            output += (f"<b>Average: </b> ({float(mean_x), float(mean_y)})<br>")
        if show_individual:
            for mask in cell_labels:
                output += (f"Mask {mask}: {cell_centers[mask]}<br>")
            output += ("<br>")
    
    if show_intensity and color_mode == "Average":
        output += ("<b>Intensities from Greyscale</b><br>")
        if show_average:
            output += (f"<b>Average: </b> {mean_cell_intensity}<br>")
        if show_individual:
            for mask in cell_labels:
                output += (f"Mask {mask}: {cell_intensities[mask]}<br>")
            output += ("<br>")

    if show_intensity and color_mode == "Red":
        output += ("<b>Red Channel Intensities </b><br>")
        if show_average:
            output += (f"<b>Average: </b> {mean_red_intensity}<br>")
        if show_individual:
            for mask in cell_labels:
                output += (f"Mask {mask}: {cell_rgb_intensities[mask]['Red']}<br>")
            output += ("<br>")
    if show_intensity and color_mode == "Green":
        output += ("<b>Green Channel Intensities </b><br>")
        if show_average:
            output += (f"<b>Average: </b> {mean_green_intensity}<br>")
        if show_individual:
            for mask in cell_labels:
                output += (f"Mask {mask}: {cell_rgb_intensities[mask]['Green']}<br>")
            output += ("<br>")
    if show_intensity and color_mode == "Blue":
        output += ("<b>Blue Channel Intensities </b><br>")
        if show_average:
            output += (f"<b>Average: </b> {mean_blue_intensity}<br>")
        if show_individual:
            for mask in cell_labels:
                output += (f"Mask {mask}: {cell_rgb_intensities[mask]['Blue']}<br>")
            output += ("<br>")



    if output == "":
        output += ("Hello there! It seems that no data has appeared :(<br>Try selecting one of the features!")

    return output


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

@app.route("/show_data", methods=["POST"])
def show_data():
    data = request.json
    print(f"Received data: {data}")  # Debugging check

    img_path, npy_path = choose_image(
    data.get("image_choice1", False), 
    data.get("image_choice2", False), 
    data.get("image_choice3", False))

    image_choice1 = data.get("image_choice1", True)
    image_choice2 = data.get("image_choice2", False)
    image_choice3 = data.get("image_choice3", False)
    show_average = data.get("show_average", True)
    show_individual = data.get("show_individual", False)
    show_sizes = data.get("show_sizes", False)
    show_cellcenters = data.get("show_cellcenters", False)
    show_intensity = data.get("show_intensity", False)
    color_mode = data.get("color_mode", "Average")

    paragraph = compile_feature_data(image_choice1, image_choice2, image_choice3, show_average, show_individual, show_sizes, show_cellcenters, show_intensity, color_mode)
    return jsonify({
        "img": img_path,
        "text": f"<p>{paragraph}</p>"
    })



@app.route("/open_wholeimage")
def open_wholeimage():
    generate_image("", "Original", False, False, False, 1, 0.5, 1, False, True, False, False)  # Ensure image is generated
    return render_template("wholeimage.html", image_path="/static/figures/w_generated_image.png")

@app.route("/open_featureex")
def open_featureex():
    compile_feature_data(True, False, False, True, False, False, False, False, "Average")
    return render_template("featureex.html")

@app.route("/open_blip")
def open_blip():
    return render_template("blip.html")

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
