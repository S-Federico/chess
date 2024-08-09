# obiettivo:
# - individuare le mosse legali
# - valutare la posizione per ogni mossa legale
# - restituire la (o le) mossa migliore

import math
from Board import Board


class CustomEngine:
    def __init__(self, board: Board):
        self.board = board

    def get_boards_tree(self, depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=True):
        if depth == 0 or self.board.is_game_finished():
            evaluation = self.board.get_evaluation()
            return evaluation[0] - evaluation[1]  # Differenza tra valutazione bianca e nera

        if maximizing_player:
            max_eval = -math.inf
            for child_board in self.board.generate_possible_boards():
                engine = CustomEngine(child_board)
                eval = engine.get_boards_tree(depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for child_board in self.board.generate_possible_boards():
                engine = CustomEngine(child_board)
                eval = engine.get_boards_tree(depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self):
        best_move = None
        best_value = -math.inf if self.board.turn == "w" else math.inf

        for child_board in self.board.generate_possible_boards():
            engine = CustomEngine(child_board)
            board_value = engine.get_boards_tree(depth=3, maximizing_player=self.board.turn == "w")
            if self.board.turn == "w" and board_value > best_value:
                best_value = board_value
                best_move = child_board.moves_log[-1]  # Assuming last move is the one that led to this board
            elif self.board.turn == "b" and board_value < best_value:
                best_value = board_value
                best_move = child_board.moves_log[-1]

        return best_move
