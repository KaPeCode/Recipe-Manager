# 1. Open Terminal and go to your project folder:
#  cd ~/Desktop/python_files/recipe_app
# 2. Activate the virtual environment:
# python3 -m venv venv
#  source venv/bin/activate
# 3. Run your app:
#  python app.py


from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Path for saving images
UPLOAD_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

FILENAME = 'recipes.json'

# --- File Handling ---
def load_recipes():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            return json.load(file)
    return {"salads": [], "mains": [], "desserts": []}

def save_recipes(data):
    with open(FILENAME, 'w') as file:
        json.dump(data, file, indent=4)



# --- Helper function for image validation ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- Routes ---
@app.route('/')
def index():
    recipes = load_recipes()
    return render_template('index.html', recipes=recipes)

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        data = load_recipes()
        category = request.form['category']
        new_recipe = {
            "title": request.form['title'],
            "ingredients": request.form['ingredients'],
            "instructions": request.form['instructions']
        }
        
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_recipe["image"] = url_for('static', filename='images/' + filename)
        
        data[category].append(new_recipe)
        save_recipes(data)
        return redirect('/')
    
    return render_template('add.html')



# Delete recipe    
@app.route('/delete/<category>/<int:index>', methods=['POST'])
def delete_recipe(category, index):
    data = load_recipes()
    if category in data and 0 <= index < len(data[category]):
        data[category].pop(index)
        save_recipes(data)
    return redirect('/')


@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    results = {"salads": [], "mains": [], "desserts": []}
    data = load_recipes()

    for category, recipes in data.items():
        for recipe in recipes:
            if query in recipe['title'].lower() or query in recipe['ingredients'].lower():
                results[category].append(recipe)

    return render_template('index.html', recipes=results)

# Edit recipe
@app.route('/edit/<category>/<int:index>', methods=['GET', 'POST'])
def edit_recipe(category, index):
    data = load_recipes()
    if category not in data or not (0 <= index < len(data[category])):
        return redirect('/')

    recipe = data[category][index]

    if request.method == 'POST':
        recipe['title'] = request.form['title']
        recipe['ingredients'] = request.form['ingredients']
        recipe['instructions'] = request.form['instructions']

        # If new image is uploaded
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                recipe["image"] = url_for('static', filename='images/' + filename)

        data[category][index] = recipe
        save_recipes(data)
        return redirect('/')

    return render_template('edit.html', recipe=recipe, category=category, index=index)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
