from flask import Flask, flash, redirect, render_template, request, jsonify, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
#from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from flask import Response

uri = "mongodb+srv://groupiespizzaadmin:Groupies12345@cluster0.3iw3bwg.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

app = Flask(__name__, template_folder='templates')
app.config['MONGO_URI'] = 'mongodb+srv://groupiespizzaadmin:Groupies12345@cluster0.3iw3bwg.mongodb.net/?retryWrites=true&w=majority'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mongo = PyMongo(app)

db = client.groupies
coll = db.groupies
users=db.users

def item_serializer(item):
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "price": item["price"],
        "image": item["image"]
    }

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/menu')
def menu():
    items = db.items.find()
    return render_template('menu.html', items=items)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = users.find_one({'username': username})

        if admin is not None and password == admin['password']:
            return redirect('admin')
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        items = db.items.find()
        return render_template('admin.html', items=items)
    
    if request.method == 'POST':
        items = db.items.find()
        newName = request.form.get('newName')
        newPrice = request.form.get('newPrice')
        
        if newName and newPrice and 'newImage' in request.files:
            newImage = request.files['newImage']
            fs = GridFS(db)
            image_id = fs.put(newImage, filename=newImage.filename, content_type=newImage.content_type)
            db.items.insert_one({'name': newName, 'price': newPrice, 'image': newImage.filename, 'image_id': image_id})
            flash('Item added successfully', 'success')
        else:
            flash('Please fill in all the fields and provide an image', 'danger')

        return render_template('admin.html', items=items)
    
@app.route('/image/<filename>')
def image(filename):
    fs = GridFS(db)
    image = fs.find_one({'filename': filename})
    if image:
        return Response(image.read(), content_type=image.content_type)
    else:
        return "Image not found", 404
    
@app.route('/register')
def register():
    if request.method==('GET'):
        return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)