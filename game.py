import json
import random
import flask

with open("words.json", "r") as f:
    words = json.load(f)

categories = [cat for cat in words]
app = flask.Flask(__name__)

def get_random_word(category):
    if category not in words:
        raise ValueError("Category not found")
    return random.choice(words[category])

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create_game():
    return flask.render_template("create_game.html", categories=categories)


if __name__ == "__main__":
    app.run(debug=True)