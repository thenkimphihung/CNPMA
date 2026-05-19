import os
from flask import Flask, render_template, request, jsonify

# Đoạn code sửa lỗi TemplateNotFound tự động tìm đường dẫn tuyệt đối:
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_folder)

# --- GIỮ NGUYÊN KHÚC CODE PHÍA DƯỚI CỦA BẠN ---
products = [
    {"id": 1, "name": "Espresso", "price": 35000, "category_id": 1, "status": "available", "image_url": "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=600&q=80"},
    {"id": 2, "name": "Cappuccino", "price": 55000, "category_id": 1, "status": "available", "image_url": "https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=600&q=80"}
]

@app.route('/')
def index():
    return render_template('shopcaffe.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    new_data = request.json
    products.append(new_data)
    return jsonify({"message": "Thêm thành công!", "data": new_data}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)