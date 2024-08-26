from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
from bson import ObjectId
import io
from PIL import Image
import gridfs

app = Flask(__name__)

# MongoDB client and database setup
client = MongoClient('mongodb://localhost:27017/')
db = client['image_db']
avatars_collection = db['avatars']

@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if the request contains a file part
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files['image']
    image_data = image.read()

    # Insert the image into the avatars collection
    result = avatars_collection.insert_one({
        "filename": image.filename,
        "content_type": image.content_type,
        "data": image_data
    })

    # Return the unique ID of the stored image
    return jsonify({"image_id": str(result.inserted_id)}), 201

@app.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        # Convert the image ID to an ObjectId
        img_id = ObjectId(image_id)
    except Exception as e:
        return jsonify({"error": "Invalid image ID"}), 400

    # Retrieve the image document from MongoDB
    image_doc = avatars_collection.find_one({"_id": img_id})

    if image_doc:
        return send_file(
            io.BytesIO(image_doc['data']),
            mimetype=image_doc['content_type'],
            as_attachment=False,
            download_name=image_doc['filename']
        )
    else:
        return jsonify({"error": "Image not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
