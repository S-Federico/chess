from stockfish import Stockfish
import logging
from Piece import Piece


class Board:
    def __init__(self,stockfish:Stockfish):
        self.stockfish=stockfish
        # Inizializza una griglia 8x8 con None per rappresentare una scacchiera vuota
        self.griglia = [[None for _ in range(8)] for _ in range(8)]

        self.moves_log = []  # Lista per registrare le mosse

        # Posizionamento dei pezzi neri (ex bianchi)
        self.griglia[0][0] = Piece('Torre', 'nero', (0, 0), vita=5, attacco=2)
        self.griglia[0][1] = Piece('Cavallo', 'nero', (0, 1), attacco=2)
        self.griglia[0][2] = Piece('Alfiere', 'nero', (0, 2), vita=2, attacco=3)
        self.griglia[0][3] = Piece('Queen', 'nero', (0, 3), attacco=5, vita=3)
        self.griglia[0][4] = Piece('Re', 'nero', (0, 4), attacco=5)
        self.griglia[0][5] = Piece('Alfiere', 'nero', (0, 5), vita=2, attacco=3)
        self.griglia[0][6] = Piece('Cavallo', 'nero', (0, 6), attacco=2)
        self.griglia[0][7] = Piece('Torre', 'nero', (0, 7), vita=5, attacco=2)
        for i in range(8):
            self.griglia[1][i] = Piece('Pedone', 'nero', (1, i), attacco=1, vita=2)

        # Posizionamento dei pezzi bianchi (ex neri)
        self.griglia[7][0] = Piece('Torre', 'bianco', (7, 0), vita=5, attacco=2)
        self.griglia[7][1] = Piece('Cavallo', 'bianco', (7, 1), attacco=2)
        self.griglia[7][2] = Piece('Alfiere', 'bianco', (7, 2), vita=2, attacco=3)
        self.griglia[7][3] = Piece('Queen', 'bianco', (7, 3), vita=3, attacco=5)
        self.griglia[7][4] = Piece('Re', 'bianco', (7, 4), attacco=5)
        self.griglia[7][5] = Piece('Alfiere', 'bianco', (7, 5), vita=2, attacco=3)
        self.griglia[7][6] = Piece('Cavallo', 'bianco', (7, 6), attacco=2)
        self.griglia[7][7] = Piece('Torre', 'bianco', (7, 7), vita=5, attacco=2)
        for i in range(8):
            self.griglia[6][i] = Piece('Pedone', 'bianco', (6, i), vita=2, attacco=1)

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
        capture = str(c) != "Capture.NO_CAPTURE"

        moving_piece = self.griglia[rp][cp]
        target_piece = self.griglia[rm][cm]

        if capture and target_piece:
            print(f"[DEBUG] Pezzo che si muove: {moving_piece.tipo} ({moving_piece.colore})")
            print(
                f"[DEBUG] Pezzo bersaglio: {target_piece.tipo if target_piece else 'None'} ({target_piece.colore if target_piece else 'None'})")

            # Sottrai l'attacco del pezzo che si sta muovendo dalla vita del pezzo che occupa la casella
            target_piece.vita -= moving_piece.attacco
            print(f"[DEBUG] Vita rimanente del pezzo bersaglio: {target_piece.vita}")

            if target_piece.vita <= 0:
                print(f"[DEBUG] Il pezzo {target_piece.tipo} ({target_piece.colore}) è stato catturato!")
                self.griglia[rm][cm] = moving_piece  # Sposta il pezzo
                self.griglia[rp][cp] = None  # La vecchia posizione è ora vuota
                moving_piece.posizione = (rm, cm)  # Aggiorna la posizione del pezzo

        else:
            # Nessuna cattura, semplicemente esegui il movimento
            print(f"[DEBUG] Nessuna cattura. Eseguendo la mossa...")
            self.griglia[rm][cm] = self.griglia[rp][cp]  # Sposta il pezzo
            self.griglia[rp][cp] = None  # La vecchia posizione è ora vuota
            self.griglia[rm][cm].posizione = (rm, cm)  # Aggiorna la posizione del pezzo
            print(
                f"[DEBUG] Pezzo spostato: {self.griglia[rm][cm].tipo} ({self.griglia[rm][cm].colore}) alla posizione ({rm}, {cm})")

        # Controlla se il gioco è finito
        if self.is_game_finished():
            self.save_log()  # Salva il log al termine del gioco
            return True

        return False

    def generate_fen(self,nextturn):
        fen_rows = []
        for row in self.griglia:
            empty_count = 0
            fen_row = ""
            for cell in row:
                if cell is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    piece_char = self.get_piece_char(cell)
                    fen_row += piece_char
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)

        # Modifica qui per far sì che Stockfish giochi come nero
        #fen = "/".join(fen_rows) + f" {nextturn} KQkq - 0 1"
        fen = "/".join(fen_rows) + f" {nextturn} - - 0 1"
        print("FEN:",fen)
        return fen

    def get_piece_char(self, piece):
        piece_map = {
            "Re": "k" if piece.colore == "nero" else "K",
            "Queen": "q" if piece.colore == "nero" else "Q",
            "Torre": "r" if piece.colore == "nero" else "R",
            "Alfiere": "b" if piece.colore == "nero" else "B",
            "Cavallo": "n" if piece.colore == "nero" else "N",
            "Pedone": "p" if piece.colore == "nero" else "P",
        }
        return piece_map.get(piece.tipo, "?")

    def is_game_finished(self):
        # Controlla se Stockfish indica che la partita è finita
        try:
            stockfish_evaluation = self.stockfish.get_evaluation()
        except Exception as e:
            print("ERROR:", e)
            return True

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
