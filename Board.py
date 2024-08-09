import copy
import math

import logging
from Piece import Piece

class Board:
    def __init__(self):
        self.turn="w"
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
        self.griglia[7][3] = Piece('Queen', 'bianco', (7, 3), vita=6, attacco=5)
        self.griglia[7][4] = Piece('Re', 'bianco', (7, 4), attacco=5)
        self.griglia[7][5] = Piece('Alfiere', 'bianco', (7, 5), vita=2, attacco=3)
        self.griglia[7][6] = Piece('Cavallo', 'bianco', (7, 6), attacco=2)
        self.griglia[7][7] = Piece('Torre', 'bianco', (7, 7), vita=5, attacco=2)
        for i in range(8):
            self.griglia[6][i] = Piece('Pedone', 'bianco', (6, i), vita=2, attacco=1)

    def getbestmove(self, depth=3):
        best_move = None
        best_value = -math.inf if self.turn == "w" else math.inf

        def get_boards_tree(board, depth, alpha=-math.inf, beta=math.inf, maximizing_player=True):
            if depth == 0 or board.is_game_finished():
                evaluation = board.get_evaluation()
                return evaluation[0] - evaluation[1]  # Differenza tra valutazione bianca e nera

            if maximizing_player:
                max_eval = -math.inf
                for child_board in board.generate_possible_boards():
                    eval = get_boards_tree(child_board, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval
            else:
                min_eval = math.inf
                for child_board in board.generate_possible_boards():
                    eval = get_boards_tree(child_board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval

        for child_board in self.generate_possible_boards():
            board_value = get_boards_tree(child_board, depth=depth, maximizing_player=self.turn == "w")
            if self.turn == "w" and board_value > best_value:
                best_value = board_value
                best_move = child_board.moves_log[-1]  # Assuming last move is the one that led to this board
            elif self.turn == "b" and board_value < best_value:
                best_value = board_value
                best_move = child_board.moves_log[-1]

        return best_move

    def get_evaluation(self):
        white_evaluation = 0
        black_evaluation = 0

        # Valori base dei pezzi
        piece_values = {
            'Pedone': 1,
            'Cavallo': 3,
            'Alfiere': 3,
            'Torre': 5,
            'Queen': 9,
            'Re': 0  # Il Re è inestimabile, ma valutiamo la sicurezza
        }

        white_king_position = None
        black_king_position = None

        for r in range(8):
            for c in range(8):
                piece = self.griglia[r][c]
                if piece:
                    base_value = piece_values.get(piece.tipo, 0)
                    piece_value = base_value * (1 + piece.vita * 0.1) + piece.attacco * 0.5

                    # Calcola il valore in base alla posizione con Stockfish
                    stockfish_position_value = 1 #self.stockfish.get_evaluation()["position"]["value"] / 100

                    if piece.colore == 'bianco':
                        white_evaluation += piece_value + stockfish_position_value
                        if piece.tipo == 'Re':
                            white_king_position = (r, c)
                    else:
                        black_evaluation += piece_value + stockfish_position_value
                        if piece.tipo == 'Re':
                            black_king_position = (r, c)

        # Valuta la sicurezza del re per ciascun giocatore
        if white_king_position:
            white_king_safety_penalty = self.evaluate_king_threat(white_king_position, 'nero')
            white_evaluation -= white_king_safety_penalty

        if black_king_position:
            black_king_safety_penalty = self.evaluate_king_threat(black_king_position, 'bianco')
            black_evaluation -= black_king_safety_penalty

        return [white_evaluation, black_evaluation]

    def evaluate_king_threat(self, king_position, opponent_color):
        king_safety_penalty = 0
        r, c = king_position

        # Direzioni possibili di attacco
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for direction in directions:
            for i in range(1, 8):  # Massimo di 7 mosse in una direzione
                new_r = r + direction[0] * i
                new_c = c + direction[1] * i

                if 0 <= new_r < 8 and 0 <= new_c < 8:
                    piece = self.griglia[new_r][new_c]
                    if piece and piece.colore == opponent_color:
                        # Verifica se il pezzo avversario può attaccare il re
                        possible_moves = piece.get_possible_moves(self)
                        if king_position in possible_moves:
                            # Penalità pesante se il re è sotto attacco
                            king_safety_penalty += 20 * (8 - i)  # Più vicino è il pezzo, maggiore è la penalità
                        break  # Interrompe la ricerca in questa direzione se trova un pezzo
                    elif piece:
                        break  # Interrompe la ricerca se trova un pezzo dello stesso colore

        return king_safety_penalty

    def generate_possible_boards(self):
        possible_boards = []

        print(f"[DEBUG] Turno corrente: {self.turn}")

        for r in range(8):
            for c in range(8):
                piece = self.griglia[r][c]

                if piece:
                    print(f"[DEBUG] Analizzando il pezzo {piece.tipo} ({piece.colore}) alla posizione ({r}, {c})")

                if piece and ((self.turn == "w" and piece.colore == "bianco") or (
                        self.turn == "b" and piece.colore == "nero")):
                    possible_moves = piece.get_possible_moves(self)  # Passa la scacchiera corrente
                    print(
                        f"[DEBUG] Mosse possibili per {piece.tipo} ({piece.colore}) alla posizione ({r}, {c}): {possible_moves}")

                    for move in possible_moves:
                        rm, cm = move

                        if 0 <= rm < 8 and 0 <= cm < 8:  # Assicurati che la mossa sia all'interno dei limiti della scacchiera
                            target_piece = self.griglia[rm][cm]
                            if target_piece is None:
                                # Se la casella è vuota, la mossa è valida
                                print(f"[DEBUG] Mossa valida trovata: da ({r}, {c}) a ({rm}, {cm})")
                                new_board = self.copy_board()
                                new_board.makemove(r, c, rm, cm)
                                possible_boards.append(new_board)
                            elif target_piece.colore != piece.colore:
                                # Se la casella è occupata da un pezzo avversario, la mossa è valida (cattura)
                                print(f"[DEBUG] Cattura trovata: da ({r}, {c}) a ({rm}, {cm})")
                                new_board = self.copy_board()
                                new_board.makemove(r, c, rm, cm)
                                possible_boards.append(new_board)
                            else:
                                # Se la casella è occupata da un pezzo dello stesso colore, la mossa non è valida
                                print(
                                    f"[DEBUG] Mossa non valida: destinazione occupata da pezzo dello stesso colore ({rm}, {cm})")

        print(f"[DEBUG] Numero di scacchiere possibili generate: {len(possible_boards)}")

        return possible_boards

    def copy_board(self):
        # Crea una copia profonda della scacchiera e restituisce una nuova istanza della Board
        new_board = Board()
        new_board.griglia = [[copy.deepcopy(piece) for piece in row] for row in self.griglia]
        new_board.turn = self.turn
        new_board.moves_log = self.moves_log.copy()
        return new_board

    def stampa_scacchiera(self):
        print("-" * 41)

        # Stampa la scacchiera con bordi a sinistra e a destra
        for row in self.griglia:
            print("| " + " | ".join([str(piece) if piece else "  " for piece in row]) + " |")
            print("-" * 41)

    def iswhite(self, position):
        r, c = position
        if 0 <= r < 8 and 0 <= c < 8:  # Assicurati che la posizione sia all'interno dei limiti della scacchiera
            piece = self.griglia[r][c]
            print(
                f"[DEBUG] iswhite check at ({r}, {c}): {'Bianco' if piece and piece.colore == 'bianco' else 'Nero o Vuoto'}")
            if piece is not None:
                return piece.colore == "bianco"
        return False

    def makemove(self, rp, cp, rm, cm):
        # Trasforma le coordinate in notazione scacchistica (facoltativo, solo per debugging)
        move = chr(cp + ord('a')) + str(8 - rp) + chr(cm + ord('a')) + str(8 - rm)
        print(f"[DEBUG] Mossa tradotta in notazione scacchistica: {move}")

        self.moves_log.append(move)  # Registra la mossa nel log

        moving_piece = self.griglia[rp][cp]
        target_piece = self.griglia[rm][cm]

        # Cambio turno
        if self.turn == "w":
            self.turn = "b"
        else:
            self.turn = "w"

        # Determina se la mossa comporta una cattura
        capture = target_piece is not None and target_piece.colore != moving_piece.colore

        if capture:
            print(f"[DEBUG] Pezzo che si muove: {moving_piece.tipo} ({moving_piece.colore})")
            print(f"[DEBUG] Pezzo bersaglio: {target_piece.tipo} ({target_piece.colore})")

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
        white_king_present = False
        black_king_present = False

        # Controlla se entrambi i re sono presenti sulla scacchiera
        for row in self.griglia:
            for piece in row:
                if piece is not None:
                    if piece.tipo == 'Re':
                        if piece.colore == 'bianco':
                            white_king_present = True
                        elif piece.colore == 'nero':
                            black_king_present = True

        if not white_king_present:
            print("Scacco matto! Il gioco è finito. I neri vincono!")
            self.save_log()  # Salva il log al termine del gioco
            return True
        elif not black_king_present:
            print("Scacco matto! Il gioco è finito. I bianchi vincono!")
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
