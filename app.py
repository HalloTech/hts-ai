import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from PIL import Image

# Create main Flask app (for WSGI)
main_app = Flask(__name__)

# Actual app mounted at /ai
ai_app = Flask(__name__)

# Folder configs
UPLOAD_FOLDER_USER = 'static/uploads/user'
UPLOAD_FOLDER_PRODUCT = 'static/uploads/product'
RESULT_FOLDER = 'static/results'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER_USER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_PRODUCT, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

ai_app.config['UPLOAD_FOLDER_USER'] = UPLOAD_FOLDER_USER
ai_app.config['UPLOAD_FOLDER_PRODUCT'] = UPLOAD_FOLDER_PRODUCT
ai_app.config['RESULT_FOLDER'] = RESULT_FOLDER

@ai_app.route('/')
def index():
    return render_template('index.html')

@ai_app.route('/generate', methods=['POST'])
def generate():
    user_img = request.files['user_image']
    product_img = request.files['product_image']

    if user_img and product_img:
        user_filename = secure_filename(user_img.filename)
        product_filename = secure_filename(product_img.filename)

        user_path = os.path.join(UPLOAD_FOLDER_USER, user_filename)
        product_path = os.path.join(UPLOAD_FOLDER_PRODUCT, product_filename)

        user_img.save(user_path)
        product_img.save(product_path)

        user_image = Image.open(user_path)
        product_image = Image.open(product_path)

        h = min(user_image.height, product_image.height)
        user_image = user_image.resize((int(user_image.width * h / user_image.height), h))
        product_image = product_image.resize((int(product_image.width * h / product_image.height), h))

        total_width = user_image.width + product_image.width
        combined = Image.new('RGB', (total_width, h))
        combined.paste(user_image, (0, 0))
        combined.paste(product_image, (user_image.width, 0))

        result_filename = f"result_{user_filename.split('.')[0]}_{product_filename.split('.')[0]}.jpg"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        combined.save(result_path)

        user_image_path = os.path.relpath(user_path, 'static')
        product_image_path = os.path.relpath(product_path, 'static')
        result_image_path = os.path.relpath(result_path, 'static')

        return render_template('index.html', 
                               user_image_path=user_image_path, 
                               product_image_path=product_image_path,
                               result_image_path=result_image_path)

    return "Upload failed", 400

@ai_app.route('/download/<filename>')
def download(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

# Mount /ai subpath
main_app.wsgi_app = DispatcherMiddleware(main_app.wsgi_app, {
    '/ai': ai_app
})

if __name__ == '__main__':
    main_app.run(debug=True, host='0.0.0.0', port=5000)
