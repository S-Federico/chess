class Piece:
    def __init__(self, tipo, colore, posizione, vita=1, attacco=1, nmosse=1):
        self.tipo = tipo
        self.vita = vita
        self.attacco = attacco
        self.nmosse = nmosse
        self.colore = colore
        self.posizione = posizione

    def __str__(self):
        return f"{self.tipo[0].upper()}{self.colore[0].upper()}"  # Rappresenta il pezzo con le prime lettere di colore e tipo

    def get_possible_moves(self, board):
        riga, colonna = self.posizione
        mosse_possibili = []

        # Funzione per aggiungere mosse valide finché non trovi un pezzo che blocca la traiettoria
        def add_moves_in_direction(directions):
            for dr, dc in directions:
                for i in range(1, 8):
                    new_r = riga + dr * i
                    new_c = colonna + dc * i
                    if 0 <= new_r < 8 and 0 <= new_c < 8:
                        target_piece = board.griglia[new_r][new_c]
                        if target_piece is None:
                            mosse_possibili.append((new_r, new_c))
                        elif target_piece.colore != self.colore:
                            mosse_possibili.append((new_r, new_c))
                            break  # Il pezzo avversario blocca ulteriori movimenti
                        else:
                            break  # Il proprio pezzo blocca la traiettoria
                    else:
                        break  # Fuori dai limiti della scacchiera

        if self.tipo == 'Pedone':
            direction = -1 if self.colore == 'bianco' else 1  # Direzione del movimento: indietro per i bianchi, avanti per i neri
            start_row = 6 if self.colore == 'bianco' else 1
            one_step_forward = (riga + direction, colonna)

            # Verifica se il pedone può muoversi di uno
            if board.griglia[one_step_forward[0]][one_step_forward[1]] is None:
                mosse_possibili.append(one_step_forward)

            # Verifica se il pedone può muoversi di due (solo se è la prima mossa)
            if riga == start_row:
                two_steps_forward = (riga + 2 * direction, colonna)
                if board.griglia[two_steps_forward[0]][two_steps_forward[1]] is None and \
                        board.griglia[one_step_forward[0]][one_step_forward[1]] is None:
                    mosse_possibili.append(two_steps_forward)

            # Controlla catture diagonali
            for dc in [-1, 1]:
                capture_move = (riga + direction, colonna + dc)
                if 0 <= capture_move[0] < 8 and 0 <= capture_move[1] < 8:
                    target_piece = board.griglia[capture_move[0]][capture_move[1]]
                    if target_piece is not None and target_piece.colore != self.colore:
                        mosse_possibili.append(capture_move)

        elif self.tipo == 'Torre':
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            add_moves_in_direction(directions)
        elif self.tipo == 'Alfiere':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            add_moves_in_direction(directions)

        elif self.tipo == 'Cavallo':
            # Movimento del cavallo: a "L"
            mosse = [(riga + 2, colonna + 1), (riga + 2, colonna - 1), (riga - 2, colonna + 1), (riga - 2, colonna - 1),
                     (riga + 1, colonna + 2), (riga + 1, colonna - 2), (riga - 1, colonna + 2), (riga - 1, colonna - 2)]
            for mossa in mosse:
                r, c = mossa
                if 0 <= r < 8 and 0 <= c < 8:
                    mosse_possibili.append((r, c))

        elif self.tipo == 'Queen':
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            add_moves_in_direction(directions)
        elif self.tipo == 'Re':
            mosse = [(riga + 1, colonna), (riga - 1, colonna), (riga, colonna + 1), (riga, colonna - 1),
                     (riga + 1, colonna + 1), (riga + 1, colonna - 1), (riga - 1, colonna + 1), (riga - 1, colonna - 1)]
            for mossa in mosse:
                if 0 <= mossa[0] < 8 and 0 <= mossa[1] < 8:
                    mosse_possibili.append(mossa)

        return mosse_possibili


