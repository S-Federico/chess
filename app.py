from flask import Flask, render_template, request, jsonify
from stockfish import Stockfish
from Board import Board

app = Flask(__name__)

# Inizializza Stockfish
stockfish_path = "stockfish/stockfish-windows-x86-64-avx2.exe"  # Aggiorna con il percorso corretto
stockfish = Stockfish(path=stockfish_path)
stockfish.set_skill_level(20)  # Imposta il livello da 0 a 20

# Inizializza la scacchiera
board = Board(stockfish)

@app.route('/')
def index():
    return render_template('index.html', board=board)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    rp = data['rp']
    cp = data['cp']
    rm = data['rm']
    cm = data['cm']

    stockfish_move = f"{chr(cp + ord('a'))}{8 - rp}{chr(cm + ord('a'))}{8 - rm}"
    if stockfish.is_move_correct(stockfish_move):
        board.makemove(rp, cp, rm, cm)
        if board.is_game_finished():
            return jsonify(status="finished", message="Game Over!")
        else:
            return jsonify(status="ok", message="Move made.")
    else:
        return jsonify(status="error", message="Invalid move.")


@app.route('/ai_move', methods=['POST'])
def ai_move():
    move = stockfish.get_best_move()

    # Gestione delle mosse speciali (es. arrocco)
    if move in ["e1g1", "e8g8"]:  # Arrocco corto
        if move == "e1g1":
            board.makemove(0, 4, 0, 6)  # Re bianco
            board.makemove(0, 7, 0, 5)  # Torre bianca
        elif move == "e8g8":
            board.makemove(7, 4, 7, 6)  # Re nero
            board.makemove(7, 7, 7, 5)  # Torre nera
    elif move in ["e1c1", "e8c8"]:  # Arrocco lungo
        if move == "e1c1":
            board.makemove(0, 4, 0, 2)  # Re bianco
            board.makemove(0, 0, 0, 3)  # Torre bianca
        elif move == "e8c8":
            board.makemove(7, 4, 7, 2)  # Re nero
            board.makemove(7, 0, 7, 3)  # Torre nera
    else:
        cp = ord(move[0]) - ord('a')
        rp = 8 - int(move[1])
        cm = ord(move[2]) - ord('a')
        rm = 8 - int(move[3])

        board.makemove(rp, cp, rm, cm)

    if board.is_game_finished():
        return jsonify(status="finished", message="Game Over!")
    else:
        return jsonify(status="ok", message="AI move made.")


if __name__ == '__main__':
    app.run(debug=True)
