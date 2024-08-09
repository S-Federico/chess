from flask import Flask, render_template, request, jsonify
from Board import Board
import CustomEngine

app = Flask(__name__)

# Inizializza la scacchiera
board = Board()  # Non passare Stockfish

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
    print(f"[DEBUG] Turno= {board.turn}")
    print(f"[DEBUG] Ricevuto richiesta di mossa: da ({rp}, {cp}) a ({rm}, {cm})")

    # Mappa i turni 'w' e 'b' ai colori 'bianco' e 'nero'
    turno_colore = "bianco" if board.turn == "w" else "nero"

    # Verifica se la mossa è valida utilizzando la logica della classe `Board`
    if board.griglia[rp][cp] is not None and board.griglia[rp][cp].colore == turno_colore:
        print(f"[DEBUG] Mossa valida per il pezzo {board.griglia[rp][cp].tipo} ({board.griglia[rp][cp].colore})")
        possible_moves = board.griglia[rp][cp].get_possible_moves(board)
        print(f"[DEBUG] Mosse possibili per il pezzo: {possible_moves}")

        if (rm, cm) in possible_moves:
            print(f"[DEBUG] Mossa scelta è valida: da ({rp}, {cp}) a ({rm}, {cm})")
            board.makemove(rp, cp, rm, cm)
            fen = board.generate_fen("b" if board.turn == "w" else "w")
            print(f"[DEBUG] FEN generata: {fen}")
            board.stampa_scacchiera()
            if board.is_game_finished():
                print(f"[DEBUG] Gioco finito!")
                return jsonify(status="finished", message="Game Over!")
            else:
                return jsonify(status="ok", message="Move made.")
        else:
            print(f"[DEBUG] Mossa scelta non è valida.")
    else:
        print(f"[DEBUG] Mossa non valida: il pezzo selezionato non appartiene al turno corrente o la posizione è vuota.")

    board.stampa_scacchiera()
    return jsonify(status="error", message="Invalid move.")

@app.route('/ai_move', methods=['POST'])
def ai_move():
    move = board.getbestmove()
    print(f"[DEBUG] mossa di catfish: {move}")

    if move:
        cp = ord(move[0]) - ord('a')
        rp = 8 - int(move[1])
        cm = ord(move[2]) - ord('a')
        rm = 8 - int(move[3])

        board.makemove(rp, cp, rm, cm)

        fen = board.generate_fen("w" if board.turn == "b" else "b")
        board.stampa_scacchiera()
        if board.is_game_finished():
            return jsonify(status="finished", message="Game Over!")
        else:
            return jsonify(status="ok", message="AI move made.")
    else:
        return jsonify(status="error", message="No valid move found.")


if __name__ == '__main__':
    app.run(debug=True)
