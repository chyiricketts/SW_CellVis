from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)

def generate_image(crop_size, color_mode, overlay_mask):
    """Generate an image with optional mask overlay"""
    img = np.random.rand(crop_size, crop_size, 3)  # Random color image
    if color_mode == "Greyscale":
        img = np.mean(img, axis=2)  # Convert to grayscale

    fig, ax = plt.subplots()
    ax.imshow(img, cmap="gray" if color_mode == "Greyscale" else None)

    # Overlay mask if enabled
    if overlay_mask:
        mask = np.zeros((crop_size, crop_size))
        mask[crop_size//4:3*crop_size//4, crop_size//4:3*crop_size//4] = 1  # Example square mask
        ax.imshow(mask, cmap="Reds", alpha=0.5)  # Red semi-transparent overlay

    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_base64

@app.route("/")
def index():
    img_base64 = generate_image(200, "Original", False)
    return render_template("singleimage.html", image_data=f"data:image/png;base64,{img_base64}")

    
    #return render_template("singleimage.html")

@app.route("/update_graph", methods=["POST"])
def update_graph():
    data = request.json
    crop_size = int(data.get("crop_size", 200))
    color_mode = data.get("color_mode", "Original")
    overlay_mask = data.get("overlay_mask", False)
    
    img_base64 = generate_image(crop_size, color_mode, overlay_mask)
    return jsonify({"image": f"data:image/png;base64,{img_base64}"})

if __name__ == "__main__":
    app.run(debug=True)
