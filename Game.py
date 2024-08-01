from stockfish import Stockfish

from Board import Board


def player_turn(board, stockfish):
    board.stampa_scacchiera()

    correct = False
    while not correct:
        try:
            pezzo = input("Inserire la posizione del pezzo da muovere (riga colonna): ")
            rp, cp = map(int, pezzo.split())

            if not (0 <= rp < 8 and 0 <= cp < 8):
                raise ValueError("Posizione fuori dai limiti della scacchiera")

            posizione = input("Inserire la prossima mossa (riga colonna): ")
            rm, cm = map(int, posizione.split())

            if not (0 <= rm < 8 and 0 <= cm < 8):
                raise ValueError("Posizione fuori dai limiti della scacchiera")

            # Costruzione della mossa in notazione scacchistica
            move = chr(cp + ord('a')) + str(8 - rp) + chr(cm + ord('a')) + str(8 - rm)

            # Verifica se la mossa è legale
            correct = stockfish.is_move_correct(move)

            if correct:
                board.makemove(rp, cp, rm, cm)
            else:
                print("Mossa non valida, riprova.")

        except ValueError as e:
            print(f"Input non valido: {e}. Per favore inserisci due interi validi separati da uno spazio.")
        except Exception as e:
            print(f"Si è verificato un errore: {e}. Per favore riprova.")

        board.stampa_scacchiera()


def ai_turn(board,stockfish):
    True
    #chiedi a stockfish
    move=stockfish.get_best_move()

    # Trasforma la mossa (es. 'e2e4') in rp, cp, rm, cm
    cp = ord(move[0]) - ord('a')  # Converti colonna da lettera a indice
    rp = 8 - int(move[1])  # Converti riga in indice
    cm = ord(move[2]) - ord('a')  # Converti colonna da lettera a indice
    rm = 8 - int(move[3])  # Converti riga in indice

    #cambia la board
    board.makemove(rp, cp, rm, cm)
    board.stampa_scacchiera()



finished=False
#avvia stockfish
stockfish_path = r"stockfish/stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(path=stockfish_path)
stockfish.set_skill_level(20)  # Imposta il livello da 0 a 20
#istanzia la scacchiera
board=Board(stockfish)

while(not finished):
    #player turn
    player_turn(board,stockfish)
    finished=board.is_game_finished()
    #ai turn
    ai_turn(board,stockfish)
    #finished check
    finished=board.is_game_finished()
