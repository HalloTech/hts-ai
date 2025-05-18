import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

# Folder configs
UPLOAD_FOLDER_USER = 'static/uploads/user'
UPLOAD_FOLDER_PRODUCT = 'static/uploads/product'
RESULT_FOLDER = 'static/results'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER_USER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_PRODUCT, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER_USER'] = UPLOAD_FOLDER_USER
app.config['UPLOAD_FOLDER_PRODUCT'] = UPLOAD_FOLDER_PRODUCT
app.config['RESULT_FOLDER'] = RESULT_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    user_img = request.files['user_image']
    product_img = request.files['product_image']

    if user_img and product_img:
        # Save uploaded images
        user_filename = secure_filename(user_img.filename)
        product_filename = secure_filename(product_img.filename)

        user_path = os.path.join(UPLOAD_FOLDER_USER, user_filename)
        product_path = os.path.join(UPLOAD_FOLDER_PRODUCT, product_filename)

        user_img.save(user_path)
        product_img.save(product_path)

        # Open and resize images to same height
        user_image = Image.open(user_path)
        product_image = Image.open(product_path)

        # Resize to same height for better alignment
        h = min(user_image.height, product_image.height)
        user_image = user_image.resize((int(user_image.width * h / user_image.height), h))
        product_image = product_image.resize((int(product_image.width * h / product_image.height), h))

        # Combine side by side
        total_width = user_image.width + product_image.width
        combined = Image.new('RGB', (total_width, h))
        combined.paste(user_image, (0, 0))
        combined.paste(product_image, (user_image.width, 0))

        # Save combined image
        result_filename = f"result_{user_filename.split('.')[0]}_{product_filename.split('.')[0]}.jpg"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        combined.save(result_path)

        return render_template('index.html', 
                               user_image_path=user_path, 
                               product_image_path=product_path,
                               result_image_path=result_path)

    return "Upload failed", 400


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')