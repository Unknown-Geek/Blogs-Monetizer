from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from backend.services.init import blog_service, seo_service, image_service, social_service

app = Flask(__name__)
CORS(app)

@app.route('/api/generate-blog', methods=['POST'])
def generate_blog():
    data = request.json
    try:
        content = blog_service.generate_blog_content(data['prompt'])
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-seo', methods=['POST'])
def analyze_seo():
    data = request.json
    try:
        report = seo_service.analyze_seo(data['content'])
        return jsonify({'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    try:
        image_path = image_service.generate_image(data['prompt'])
        return jsonify({'image_path': image_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/publish', methods=['POST'])
def publish():
    data = request.json
    try:
        result = blog_service.publish_blog(
            data['title'],
            data['content'],
            data['image_path'],
            data['labels']
        )
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)