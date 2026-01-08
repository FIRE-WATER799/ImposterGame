import json
import random
import flask
import flask_sqlalchemy
from flask import redirect, render_template, request, jsonify

with open("words.json", "r") as f:
    words = json.load(f)

categories = [cat for cat in words]
app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
db = flask_sqlalchemy.SQLAlchemy(app)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    imposterammount = db.Column(db.Integer, nullable=False)
    imposters = db.Column(db.PickleType, nullable=False)
    word = db.Column(db.String(120), nullable=False)
    players = db.Column(db.PickleType, nullable=False)
    gameName = db.Column(db.String(120), nullable=True)
    gameType = db.Column(db.String(20), nullable=False)
    gameState = db.Column(db.String(20), nullable=False, default="waiting")
    currentPlayer = db.Column(db.String(80), nullable=True)
    playerOrder = db.Column(db.PickleType, nullable=True)
    currentPlayerIndex = db.Column(db.Integer, default=0)
    eliminated = db.Column(db.PickleType, nullable=True, default=list)
    winner = db.Column(db.String(20), nullable=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

def get_random_word(category):
    if category not in words:
        raise ValueError("Category not found")
    return random.choice(words[category])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/join", methods=["GET", "POST"])
def join_game():
    if flask.request.method == "GET":
        return render_template("join_game.html")
    
    if flask.request.method == "POST":
        data = request.get_json()
        code = int(data.get("code"))
        playerName = data.get("playerName")
        
        game = Game.query.filter_by(code=code).first()
        if not game:
            return {"error": "Game not found"}, 404
        
        if game.gameType != "online":
            return {"error": "This is not an online game"}, 400
        
        if playerName in game.players:
            return {"error": "Player name already in game"}, 400
        
        players = game.players.copy() if game.players else []
        players.append(playerName)
        game.players = players
        db.session.commit()
        
        return {"code": code, "status": "joined"}

@app.route("/create", methods=["GET", "POST"])
def create_game():
    if flask.request.method == "POST":
        data = request.get_json()
        categories_list = data.get("categories")
        
        if not categories_list:
            return {"error": "Must select at least one category"}, 400
        
        category = random.choice(categories_list)
        impostersammount = int(data.get("imposters", 1))
        word = get_random_word(category)
        code = random.randint(1000, 9999)
        gameName = data.get("gameName", f"Game {code}")
        playerName = data.get("playerName")
        
        GameInstance = Game(
            category=category,
            imposterammount=impostersammount,
            imposters=[],
            word=word,
            players=[playerName],
            code=code,
            gameName=gameName,
            gameType="online",
            eliminated=[]
        )
        db.session.add(GameInstance)
        db.session.commit()
        return {"code": code}
    
    if flask.request.method == "GET":
        return render_template("create_game.html", categories=categories)

@app.route("/create_local", methods=["GET", "POST"])
def create_local_game():
    if flask.request.method == "POST":
        data = request.get_json()
        code = random.randint(10000, 19999)
        categories_list = data.get("categories")
        
        if categories_list:
            category = random.choice(categories_list)
        else:
            category = random.choice(categories)
        
        impostersammount = int(data.get("imposters", 1))
        word = get_random_word(category)
        players = data.get("players", [])
        
        if len(players) < 2:
            return {"error": "Need at least 2 players"}, 400
        
        if impostersammount >= len(players):
            return {"error": "Too many imposters"}, 400
        
        imposters = random.sample(players, impostersammount)
        
        GameInstance = Game(
            category=category,
            code=code,
            imposterammount=impostersammount,
            imposters=imposters,
            word=word,
            players=players,
            gameType="local",
            gameName=data.get("gameName", f"Local Game {code}"),
            playerOrder=players,
            eliminated=[]
        )
        db.session.add(GameInstance)
        db.session.commit()
        return {"code": code}

    if flask.request.method == "GET":
        return render_template("create_local_game.html", categories=categories)

@app.route("/game/<int:code>", methods=["GET", "POST"])
def game_page(code):
    if flask.request.method == "GET":
        game = Game.query.filter_by(code=code).first()
        if not game:
            return "Game not found", 404
        
        playerName = request.args.get('player')
        
        gameData = {
            "id": game.id,
            "code": game.code,
            "category": game.category,
            "imposterammount": game.imposterammount,
            "imposters": game.imposters,
            "word": game.word,
            "players": [
                {
                    "name": p,
                    "isImposter": p in game.imposters,
                    "eliminated": p in (game.eliminated or [])
                }
                for p in game.players
            ],
            "gameName": game.gameName,
            "gameType": game.gameType,
            "gameState": game.gameState,
            "currentPlayer": game.currentPlayer,
            "currentPlayerName": playerName,
            "winner": game.winner
        }

        return render_template("game.html", game_data=gameData)

    if flask.request.method == "POST":
        data = request.get_json()
        game = Game.query.filter_by(code=code).first()
        if not game:
            return {"error": "Game not found"}, 404
        
        action = data.get("action")
        
        if action == "start":
            if game.gameType == "online" and len(game.players) < 2:
                return {"error": "Need at least 2 players"}, 400
            game.gameState = "playing"
            if not game.playerOrder:
                game.playerOrder = game.players.copy()
            if not game.imposters:
                game.imposters = random.sample(game.players, min(game.imposterammount, len(game.players)))
            game.currentPlayerIndex = 0
            game.currentPlayer = game.playerOrder[0] if game.playerOrder else None
        
        elif action == "next_player":
            if game.playerOrder:
                available_players = [p for p in game.playerOrder if p not in (game.eliminated or [])]
                if available_players:
                    current_idx = available_players.index(game.currentPlayer) if game.currentPlayer in available_players else 0
                    next_idx = (current_idx + 1) % len(available_players)
                    game.currentPlayer = available_players[next_idx]
        
        elif action == "eliminate":
            player_to_eliminate = data.get("playerName")
            if player_to_eliminate:
                eliminated = game.eliminated.copy() if game.eliminated else []
                if player_to_eliminate not in eliminated:
                    eliminated.append(player_to_eliminate)
                game.eliminated = eliminated
                
                remaining_imposters = [p for p in game.imposters if p not in game.eliminated]
                remaining_players = [p for p in game.players if p not in game.eliminated]
                
                if not remaining_imposters:
                    game.gameState = "won"
                    game.winner = "civilians"
                elif len(remaining_imposters) >= len(remaining_players) - len(remaining_imposters):
                    game.gameState = "lost"
                    game.winner = "imposters"
        
        elif action == "end":
            game.gameState = "ended"
        
        else:
            game.gameState = data.get("gameState", game.gameState)
            game.currentPlayer = data.get("currentPlayer", game.currentPlayer)
        
        db.session.commit()
        return {"status": "success"}

@app.route("/api/game/<int:code>", methods=["GET"])
def get_game_data(code):
    game = Game.query.filter_by(code=code).first()
    if not game:
        return {"error": "Game not found"}, 404
    
    playerName = request.args.get('player')
    
    return jsonify({
        "id": game.id,
        "code": game.code,
        "category": game.category,
        "imposterammount": game.imposterammount,
        "imposters": game.imposters,
        "word": game.word,
        "players": [
            {
                "name": p,
                "isImposter": p in game.imposters,
                "eliminated": p in (game.eliminated or [])
            }
            for p in game.players
        ],
        "gameName": game.gameName,
        "gameType": game.gameType,
        "gameState": game.gameState,
        "currentPlayer": game.currentPlayer,
        "currentPlayerName": playerName,
        "winner": game.winner,
        "eliminated": game.eliminated or []
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)