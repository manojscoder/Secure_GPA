from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import random
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'pro'


client = MongoClient('mongodb://localhost:27017/')
db = client['project']
sign_up_collection = db['sign_up_data']


@app.route('/sign_up_page')
def signUpPage():
    return render_template('signup.html')

@app.route('/success')
def success():
    return "<h1>Valid user</h1>"

@app.route('/unsuccessful')
def unsuccessful():
    return "<h1>Invalid user</h1>"

@app.route('/login_page')
def loginPage():
    return render_template('login.html')

@app.route('/set_username2', methods=['POST'])
def set_username2():

    username = request.form.get('username')
    verify = sign_up_collection.find_one({'username': username})

    if not verify:
        return render_template('start.html', message='User doesnt exist please create new account')
    
    session['username'] = username
    session['pin'] = verify['pin']
    return redirect(url_for('images1'))



def load_images():
    image_folder = 'static/images'
    images = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
    return images


@app.route('/images1', methods=['GET'])
def images1():
    images = load_images()
    random.shuffle(images)
    session['images'] = images
    return render_template('image_2.html', images=images)

count = 1

@app.route('/select_image1', methods=['POST'])
def select_image1():
    global selected_images, count
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    image = request.json['image']
    pin = str(session['pin'])

    if pin and int(pin[0]) == count:
        forward = pin[1]
        session['pin'] = pin[2:]
        index = (session['images'].index(image) - int(forward)) % 25
        selected_images.append(session['images'][index])

    count += 1

    if count < 6:
        images = load_images()
        random.shuffle(images)
        session['images'] = images
        return jsonify({'status': 'success', 'images': images})
    else:
        details = sign_up_collection.find_one({'username': session['username']})
        if selected_images[0] == details['image1'] and selected_images[1] == details['image2'] and selected_images[2] == details['image3']:
            selected_images = []
            return jsonify({'status': 'completed'})
    
        selected_images = []
        return jsonify({'status': 'not completed'})



selected_images = []


@app.route('/')
def index():
    return render_template('start.html')





@app.route('/set_username1', methods=['POST'])
def set_username1():

    username = request.form.get('username')
    pin = request.form.get('pin')
    verify = sign_up_collection.find_one({'username': username})

    if verify:
        return render_template('signup.html', message='User already exists')
    
    session['username'] = username
    session['pin'] = pin
    return redirect(url_for('images'))





@app.route('/images', methods=['GET'])
def images():
    images = load_images()
    random.shuffle(images)
    return render_template('image_1.html', images=images)

@app.route('/select_image', methods=['POST'])
def select_image():
    global selected_images
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    image = request.json['image']
    selected_images.append(image)

    if len(selected_images) < 3:
        images = load_images()
        random.shuffle(images)
        return jsonify({'status': 'success', 'images': images})
    else:
        username = session['username']
        pin = session['pin']
        sign_up_collection.insert_one({'username': username, 'pin': pin, 'image1': selected_images[0], 'image2': selected_images[1], 'image3': selected_images[2]})
        selected_images = []
        return jsonify({'status': 'completed'})



if __name__ == '__main__':
    app.run(debug=True)
