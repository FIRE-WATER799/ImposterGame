import json
import random
import flask
import flask_sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column

with open("words.json", "r") as f:
    words = json.load(f)

categories = [cat for cat in words]
app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
db = flask_sqlalchemy.SQLAlchemy(app)

class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[int] = mapped_column(unique=True)
    category: Mapped[str] = mapped_column(db.String(80))
    imposters: Mapped[list] = mapped_column()
    word: Mapped[str] = mapped_column(db.String(120))
    players: Mapped[list] = mapped_column()
    gameName: Mapped[str] = mapped_column(db.String(120), nullable=True)
    gameState: Mapped[str] = mapped_column(db.String(20), default="waiting")

def get_random_word(category):
    if category not in words:
        raise ValueError("Category not found")
    return random.choice(words[category])

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create_game():
    if flask.request.method == "POST":
        data = flask.request.json
        category = data.get("category")
        impostersammount = data.get("imposters")
        word = get_random_word(category)
        code = random.randint(0000, 9999)
        gameName = data.get("gameName", f"Game {code}")
        playerName = data.get("playerName")
        GameInstance = Game(
            category=category,
            imposters=[],
            word=word,
            players=[playerName],
            code=code,
            gameName=gameName
        )
        db.session.add(GameInstance)
        db.session.commit()
        return 201

    if flask.request.method == "GET":
        return flask.render_template("create_game.html", categories=categories)


if __name__ == "__main__":
    app.run(debug=True)