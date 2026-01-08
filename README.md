# 🎭 Imposter Game

A fun party game where players must find the imposter among them. The imposter knows only the category while others know the secret word. Players take turns giving clues, and everyone votes to eliminate who they think is the imposter.

## Features

- **Online Games**: Create and join games with friends online using game codes
- **Local Games**: Play with friends sitting together with role assignments
- **Dynamic Word Revealing**: Gradually reveal letters of the secret word
- **Imposter Detection**: Identify who the imposter is through discussion and voting
- **Game States**: Waiting, Playing, Won (civilians found imposters), Lost (imposters survived)

## Installation

### Requirements
- Python 3.8+
- Flask
- Flask-SQLAlchemy

### Setup

1. Clone the repository:
```bash
cd /workspaces/ImposterGame
```

2. Install dependencies (if not already installed):
```bash
pip install flask flask-sqlalchemy
```

3. Initialize the database:
```bash
python db_create.py
```

4. Run the application:
```bash
python game.py
```

The application will start at `http://localhost:5000`

## How to Play

### Online Game (with players in different locations)

1. **Host creates a game**:
   - Visit the home page and click "Create Game"
   - Select number of imposters
   - Select categories for word selection
   - Enter your player name
   - Submit to create the game
   - Share the game code with other players

2. **Players join the game**:
   - Click "Join Game" from the home page
   - Enter the game code
   - Enter your player name
   - Click "Join Game"

3. **Start the game**:
   - Once all players have joined, click "Start Game"
   - The game will randomly assign imposters and select a word

4. **Play**:
   - Each player takes a turn revealing the word (civilians) or category (imposters)
   - Non-impostors can gradually reveal letters of the word
   - Imposters see only the category
   - Give clues to help find the imposter or mislead if you're the imposter
   - Click "Next Player" to advance turns

5. **Vote to eliminate**:
   - During gameplay, select a player from the dropdown and click "Vote to Eliminate"
   - If you eliminate an impostor, you get closer to winning
   - If all imposters are eliminated before they outnumber civilians, civilians win
   - If imposters equal or outnumber civilians, imposters win

### Local Game (with players together)

1. **Create a local game**:
   - Click "Play Game" under Local Game on the home page
   - Enter number of imposters
   - Select categories (optional)
   - Add all player names
   - Submit to create the game

2. **Game shows player roles**:
   - Imposters can see the category
   - Non-imposters can see the word
   - Players can view their own role by clicking "Reveal Word"

3. **Play the same way**:
   - Take turns giving clues
   - Vote to eliminate suspected imposters
   - Win conditions are the same as online games

## Game Rules

- **Civilians**: Know the secret word, must identify the imposter through discussion
- **Imposters**: Know only the category, must avoid being caught and try to eliminate civilians
- **Word Reveals**: Non-imposters can gradually reveal letters to help themselves
- **Winning**: 
  - Civilians win if all imposters are eliminated
  - Imposters win if they equal or outnumber the non-imposters

## API Endpoints

### Create Game
- **POST** `/create`
- Creates an online game
- **Body**: 
  ```json
  {
    "imposters": "1",
    "categories": ["Food", "Animals"],
    "playerName": "Alice",
    "gameName": "Game Night"
  }
  ```
- **Response**: `{"code": 1234}`

### Join Game
- **POST** `/join`
- Join an online game
- **Body**: 
  ```json
  {
    "code": "1234",
    "playerName": "Bob"
  }
  ```
- **Response**: `{"code": 1234, "status": "joined"}`

### Create Local Game
- **POST** `/create_local`
- Creates a local game with pre-defined players
- **Body**: 
  ```json
  {
    "imposters": "2",
    "categories": ["Food"],
    "players": ["Alice", "Bob", "Charlie"],
    "gameName": "Local Game"
  }
  ```
- **Response**: `{"code": 10234}`

### Get Game Page
- **GET** `/game/<code>`
- View game page
- **Query**: `?player=PlayerName` (optional, for tracking current player)

### Game Actions
- **POST** `/game/<code>`
- Perform game actions
- **Body Examples**:
  ```json
  {"action": "start"}
  {"action": "next_player"}
  {"action": "eliminate", "playerName": "Alice"}
  {"action": "end"}
  ```

### Get Game Data (API)
- **GET** `/api/game/<code>`
- Get current game state as JSON
- **Query**: `?player=PlayerName` (optional)
- **Response**: Complete game state with all player info

## File Structure

```
ImposterGame/
├── game.py                 # Flask app and routes
├── db_create.py           # Database initialization
├── words.json             # Word categories and words
├── instance/
│   └── games.db          # SQLite database
└── templates/
    ├── index.html        # Home page
    ├── create_game.html  # Create online game
    ├── create_local_game.html  # Create local game
    ├── join_game.html    # Join game page
    └── game.html         # Main game interface
```

## Database Schema

### Game Model
- `id`: Primary key
- `code`: Unique game code (4-5 digits)
- `category`: Selected category for this game
- `imposterammount`: Number of imposters
- `imposters`: List of imposter player names
- `word`: Secret word for this game
- `players`: List of all player names
- `gameName`: Human-readable game name
- `gameType`: "online" or "local"
- `gameState`: "waiting", "playing", "won", "lost", "ended"
- `currentPlayer`: Name of player whose turn it is
- `playerOrder`: Order of players for turns
- `eliminated`: List of eliminated players
- `winner`: "civilians", "imposters", or null

## Customization

### Adding Words

Edit `words.json` to add more categories and words:

```json
{
  "MyCategory": [
    "word1",
    "word2",
    "word3"
  ]
}
```

### Styling

All CSS is embedded in the HTML templates. Edit the `<style>` sections to customize colors and layout.

## Development

To run in development mode with hot reload:
```bash
python game.py
```

The Flask development server will automatically reload when you change files.

## Known Limitations

- Single server deployment (not multi-server ready)
- In-memory imposters assignment for online games (assigned when game starts)
- No persistent game history
- No chat or real-time communication between players
- Database uses SQLite (suitable for single-deployment)

## Future Enhancements

- Real-time player updates with WebSockets
- Chat integration for in-game discussion
- Game history and statistics
- Multiple game modes (time limits, point scoring)
- User accounts and friend lists
- Mobile app

## License

MIT License

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.
