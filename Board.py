from stockfish import Stockfish
import logging
from Piece import Piece


class Board:
    def __init__(self,stockfish:Stockfish):
        self.stockfish=stockfish
        # Inizializza una griglia 8x8 con None per rappresentare una scacchiera vuota
        self.griglia = [[None for _ in range(8)] for _ in range(8)]

        self.moves_log = []  # Lista per registrare le mosse

        # Posizionamento dei pezzi bianchi
        self.griglia[0][0] = Piece('Torre', 'bianco', (0, 0))
        self.griglia[0][1] = Piece('Cavallo', 'bianco', (0, 1))
        self.griglia[0][2] = Piece('Alfiere', 'bianco', (0, 2))
        self.griglia[0][3] = Piece('Queen', 'bianco', (0, 3))
        self.griglia[0][4] = Piece('Re', 'bianco', (0, 4))
        self.griglia[0][5] = Piece('Alfiere', 'bianco', (0, 5))
        self.griglia[0][6] = Piece('Cavallo', 'bianco', (0, 6))
        self.griglia[0][7] = Piece('Torre', 'bianco', (0, 7))
        for i in range(8):
            self.griglia[1][i] = Piece('Pedone', 'bianco', (1, i))

        # Posizionamento dei pezzi neri
        self.griglia[7][0] = Piece('Torre', 'nero', (7, 0))
        self.griglia[7][1] = Piece('Cavallo', 'nero', (7, 1))
        self.griglia[7][2] = Piece('Alfiere', 'nero', (7, 2))
        self.griglia[7][3] = Piece('Queen', 'nero', (7, 3))
        self.griglia[7][4] = Piece('Re', 'nero', (7, 4))
        self.griglia[7][5] = Piece('Alfiere', 'nero', (7, 5))
        self.griglia[7][6] = Piece('Cavallo', 'nero', (7, 6))
        self.griglia[7][7] = Piece('Torre', 'nero', (7, 7))
        for i in range(8):
            self.griglia[6][i] = Piece('Pedone', 'nero', (6, i))

    def stampa_scacchiera(self):
        print("-" * 41)

        # Stampa la scacchiera con bordi a sinistra e a destra
        for row in self.griglia:
            print("| " + " | ".join([str(piece) if piece else "  " for piece in row]) + " |")
            print("-" * 41)

    def iswhite(self, position):
        piece = self.griglia[position[0]][position[1]]
        if piece is not None:
            return piece.colore == "bianco"
        return False

    def makemove(self, rp, cp, rm, cm):
        # Trasforma le coordinate in notazione scacchistica
        move = chr(cp + ord('a')) + str(8 - rp) + chr(cm + ord('a')) + str(8 - rm)
        print(f"[DEBUG] Mossa tradotta in notazione scacchistica: {move}")

        self.moves_log.append(move)  # Registra la mossa nel log

        # Controlla se la mossa comporta una cattura
        c = self.stockfish.will_move_be_a_capture(move)
        print(f"[DEBUG] La mossa comporta una cattura? {c}")
        if(str(c)=="Capture.NO_CAPTURE"):
            capture=False
        else:
            capture=True

        if capture:
            target_piece = self.griglia[rm][cm]
            moving_piece = self.griglia[rp][cp]

            print(f"[DEBUG] Pezzo che si muove: {moving_piece.tipo} ({moving_piece.colore})")
            print(
                f"[DEBUG] Pezzo bersaglio: {target_piece.tipo if target_piece else 'None'} ({target_piece.colore if target_piece else 'None'})")

            # Sottrai l'attacco del pezzo che si sta muovendo dalla vita del pezzo che occupa la casella
            target_piece.vita -= moving_piece.attacco
            print(f"[DEBUG] Vita rimanente del pezzo bersaglio: {target_piece.vita}")

            if target_piece.vita <= 0:
                print(f"[DEBUG] Il pezzo {target_piece.tipo} ({target_piece.colore}) è stato catturato!")
                # Il pezzo bersaglio è stato catturato
                self.stockfish.make_moves_from_current_position([move])
                self.griglia[rm][cm] = moving_piece  # Sposta il pezzo
                self.griglia[rp][cp] = None  # La vecchia posizione è ora vuota
                moving_piece.posizione = (rm, cm)  # Aggiorna la posizione del pezzo
            else:
                # Se il pezzo bersaglio non è morto, il movimento non viene eseguito sulla griglia
                print(f"Il pezzo {target_piece.tipo} ({target_piece.colore}) ha resistito all'attacco!")

        else:
            # Nessuna cattura, semplicemente esegui il movimento
            print(f"[DEBUG] Nessuna cattura. Eseguendo la mossa...")
            self.stockfish.make_moves_from_current_position([move])
            self.griglia[rm][cm] = self.griglia[rp][cp]  # Sposta il pezzo
            self.griglia[rp][cp] = None  # La vecchia posizione è ora vuota
            self.griglia[rm][cm].posizione = (rm, cm)  # Aggiorna la posizione del pezzo
            print(
                f"[DEBUG] Pezzo spostato: {self.griglia[rm][cm].tipo} ({self.griglia[rm][cm].colore}) alla posizione ({rm}, {cm})")

    def is_game_finished(self):
        # Controlla se Stockfish indica che la partita è finita
        stockfish_evaluation = self.stockfish.get_evaluation()

        if stockfish_evaluation['type'] == 'mate' and stockfish_evaluation['value'] == 1:
            print("Scacco matto! Il gioco è finito. I bianchi vincono!")
            self.save_log()  # Salva il log al termine del gioco
            return True
        elif stockfish_evaluation['type'] == 'mate' and stockfish_evaluation['value'] == -1:
            print("Scacco matto! Il gioco è finito. I neri vincono!")
            self.save_log()  # Salva il log al termine del gioco
            return True

        # Aggiungere altri controlli di fine partita se necessario (es. patta)
        return False

    def save_log(self):
        # Configura un logger separato per il gioco
        game_logger = logging.getLogger('game_logger')
        game_logger.setLevel(logging.INFO)

        # Crea un handler per scrivere su file
        file_handler = logging.FileHandler('game_log.txt', mode='a')
        file_handler.setFormatter(logging.Formatter('%(message)s'))

        # Aggiungi l'handler al logger
        if not game_logger.handlers:
            game_logger.addHandler(file_handler)

        game_logger.info("Log delle mosse della partita:")
        for move in self.moves_log:
            game_logger.info(move)
        game_logger.info("-" * 40)  # Separatore tra partite

        print("Log delle mosse salvato in 'game_log.txt'.")
