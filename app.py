"""
from flask import Flask, render_template, request, send_from_directory
from deepface import DeepFace
import os
import shutil

app = Flask(__name__)

DATASET = "dataset"
UPLOADS = "uploads"
MATCHES = "matches"

os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(MATCHES, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # clear previous results
        for f in os.listdir(MATCHES):
            os.remove(os.path.join(MATCHES, f))

        file = request.files["photo"]
        path = os.path.join(UPLOADS, file.filename)
        file.save(path)

        for img in os.listdir(DATASET):
            try:
                result = DeepFace.verify(
                    img1_path=path,
                    img2_path=os.path.join(DATASET, img),
                    enforce_detection=False
                )
                if result["verified"]:
                    shutil.copy(
                        os.path.join(DATASET, img),
                        os.path.join(MATCHES, img)
                    )
            except:
                pass

        return render_template("index.html", results=os.listdir(MATCHES))

    return render_template("index.html", results=[])

@app.route("/matches/<filename>")
def get_image(filename):
    return send_from_directory(MATCHES, filename)

if __name__ == "__main__":
    app.run(debug=True)
"""



from flask import Flask, render_template, request, send_from_directory
from deepface import DeepFace
from werkzeug.utils import secure_filename
import os
import shutil
import uuid

app = Flask(__name__)

DATASET = "dataset"
UPLOADS = "uploads"
MATCHES = "matches"

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(MATCHES, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        print("FORM SUBMITTED")

        # clear old matches
        for f in os.listdir(MATCHES):
            os.remove(os.path.join(MATCHES, f))

        file = request.files.get("photo")
        if not file or file.filename == "" or not allowed_file(file.filename):
            return render_template("index.html", results=[])

        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(UPLOADS, unique_name)
        file.save(upload_path)

        for img in os.listdir(DATASET):
            img_path = os.path.join(DATASET, img)
            try:
                result = DeepFace.verify(
                    img1_path=upload_path,
                    img2_path=img_path,
                    enforce_detection=False
                )
                if result.get("verified"):
                    shutil.copy(img_path, os.path.join(MATCHES, img))
            except Exception as e:
                print("Error:", e)

        return render_template("index.html", results=os.listdir(MATCHES))

    return render_template("index.html", results=[])

@app.route("/matches/<filename>")
def get_image(filename):
    return send_from_directory(MATCHES, filename)

if __name__ == "__main__":
    app.run(debug=True)


#python3.10 app.py

"""

from flask import Flask, render_template, request, send_from_directory
from deepface import DeepFace
import os
import shutil
import base64

# ---------------- APP SETUP ----------------
app = Flask(__name__)

# ---------------- FOLDERS ----------------
DATASET = "dataset"
UPLOADS = "uploads"
MATCHES = "matches"

os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(MATCHES, exist_ok=True)

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # clear previous matches
        for f in os.listdir(MATCHES):
            os.remove(os.path.join(MATCHES, f))

        # get image from camera (base64)
        image_data = request.form.get("imageData")
        if not image_data:
            return render_template("index.html", results=[])

        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        captured_image_path = os.path.join(UPLOADS, "capture.jpg")
        with open(captured_image_path, "wb") as f:
            f.write(image_bytes)

        # face matching
        for img in os.listdir(DATASET):
            dataset_img_path = os.path.join(DATASET, img)

            try:
                result = DeepFace.verify(
                    img1_path=captured_image_path,
                    img2_path=dataset_img_path,
                    enforce_detection=False
                )

                if result.get("verified"):
                    shutil.copy(
                        dataset_img_path,
                        os.path.join(MATCHES, img)
                    )

            except Exception as e:
                print("Error processing", img, ":", e)

        return render_template("index.html", results=os.listdir(MATCHES))

    return render_template("index.html", results=[])


@app.route("/matches/<filename>")
def get_image(filename):
    return send_from_directory(MATCHES, filename)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

"""