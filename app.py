import os
from flask import Flask, request, send_file
from rembg import remove
from io import BytesIO
from PIL import Image
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address




app = Flask(__name__)

# Initialize CORS 
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000","https://removeimagebackground.netlify.app", "https://removeimagebackground.site"]}})

# Set up rate limiting (100 requests per minute per client IP)
limiter = Limiter(get_remote_address, app=app, default_limits=["30 per minute"])

app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # Limit to 4MB

@app.before_request
def restrict_origin():
    allowed_origins = ["http://localhost:3000","https://removeimagebackground.netlify.app", "https://removeimagebackground.site"]
    origin = request.headers.get("Origin")
    # print(origin)
    if origin and origin not in allowed_origins:
        return {"error": "Origin not allowed"}, 403

@app.route('/')
def index():
    return "Rembg API is running."


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    print("Received request")

    if "image_file" not in request.files:
        print("No file part in the request")
        return {"error": "No file part"}, 400

    file = request.files["image_file"]

    if file.filename == "":
        print("No selected file")
        return {"error": "No selected file"}, 400

    try:
        # Read the image file
        img = Image.open(file.stream)
        print("Image file opened")

        # Remove the background
        output = remove(img)
        print("Background removed")

        # Save to a BytesIO object
        img_io = BytesIO()
        output.save(img_io, "PNG")
        img_io.seek(0)
        print("Image processed and saved to BytesIO")

        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        print(f"Error occurred: {e}", exc_info=True)  # Logs the full stack trace
        return {"error": str(e)}, 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Get the port from environment or default to 5000
    app.run(host='0.0.0.0', port=port)
