from tensorflow.keras.models import load_model
import numpy as np
import os
import chess
import random

# Load the latest trained model
def load_trained_model():
    try:
        model = load_model('my_model.keras')
        print("Model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Add your logic to use the model here
def predict(data, model):
    try:
        # Example prediction logic
        predictions = model.predict(data)
        return predictions
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

# Chess-related functions
def update_board_pieces(board):
    pieces = {}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            pieces[chess.square_name(square)] = piece.symbol()
    return pieces

# Define the board colors
def define_board_colors():
    board_colors = {}
    for square in chess.SQUARES:
        if (chess.square_rank(square) + chess.square_file(square)) % 2 == 0:
            board_colors[square] = 'white'
        else:
            board_colors[square] = 'black'
    return board_colors

def print_custom_board(board_colors, board_pieces, orientation):
    if orientation == 'black':
        ranks = range(8)
        files = range(7, -1, -1)
        file_labels = 'h g f e d c b a'
        rank_labels = '12345678'
    else:
        ranks = range(7, -1, -1)
        files = range(8)
        file_labels = 'a b c d e f g h'
        rank_labels = '87654321'

    print("     " + "    ".join(file_labels))
    for rank in ranks:
        for i in range(3):
            line = f"{rank_labels[rank]} " if i == 1 else "  "
            for file in files:
                square = chess.square(file, rank)
                piece = board_pieces.get(chess.square_name(square), " ")
                if i == 1:
                    if board_colors[square] == 'white':
                        if file == files[0]:
                            line += f"   {piece:<2}  " if piece != " " else "       "
                        else:
                            line += f"    {piece:<2}  " if piece != " " else "        "
                    else:
                        if file == files[0]:
                            line += f" ██{piece:<2}█ " if piece != " " else " █████ "
                        else:
                            line += f"  ██{piece:<2}█ " if piece != " " else "  █████ "
                else:
                    if board_colors[square] == 'white':
                        line += "       " if file == files[0] else "        "
                    else:
                        line += " █████ " if file == files[0] else "  █████ "
            if i == 1:
                line += f" {rank_labels[rank]}"
            print(line)
    print("     " + "    ".join(file_labels))

def evaluate_board(board, position_counts):
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    material_score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                material_score += value
            else:
                material_score -= value

    board_fen = board.board_fen()
    repetition_penalty = position_counts.get(board_fen, 0) * 10
    return material_score - repetition_penalty

def minimax(board, depth, alpha, beta, maximizing_player, position_counts, transposition_table):
    board_fen = board.board_fen()

    if board_fen in transposition_table:
        return transposition_table[board_fen]

    if depth == 0 or board.is_game_over():
        eval = evaluate_board(board, position_counts)
        transposition_table[board_fen] = eval
        return eval

    if maximizing_player:
        max_eval = -float('inf')
        for move in sorted(board.legal_moves, key=lambda m: m.uci()):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False, position_counts, transposition_table)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        transposition_table[board_fen] = max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for move in sorted(board.legal_moves, key=lambda m: m.uci()):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True, position_counts, transposition_table)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[board_fen] = min_eval
        return min_eval

def best_move(board, depth, position_counts, transposition_table):
    best_moves = []
    best_eval = -float('inf')
    for move in board.legal_moves:
        board.push(move)
        board_fen = board.board_fen()
        position_counts[board_fen] = position_counts.get(board_fen, 0) + 1
        move_eval = minimax(board, depth - 1, -float('inf'), float('inf'), False, position_counts, transposition_table)
        board.pop()
        position_counts[board_fen] -= 1
        if move_eval > best_eval:
            best_eval = move_eval
            best_moves = [move]
        elif move_eval == best_eval:
            best_moves.append(move)
    return random.choice(best_moves) if best_moves else None

if __name__ == "__main__":
    model = load_trained_model()

    if model is not None:
        # Example data: Replace with actual data in correct format
        data = np.random.random((1, 784))  # Replace with actual data
        
        # Perform prediction
        predictions = predict(data, model)
        if predictions is not None:
            print("Predictions:", predictions)
        else:
            print("Prediction failed.")

    board = chess.Board()
    depth = 5
    position_counts = {}
    transposition_table = {}

    color_choice = os.getenv('COLOR_CHOICE', 'w')

    if os.getenv('GITHUB_ACTIONS') is None:
        color_choice = input("Do you want to play as white or black? (w/b): ").strip().lower()

    while color_choice not in ['w', 'b']:
        color_choice = input("Invalid choice. Please enter 'w' for white or 'b' for black: ").strip().lower()

    orientation = 'black' if color_choice == 'b' else 'white'

    board_colors = define_board_colors()
    board_pieces = update_board_pieces(board)  # Initialize board_pieces here

    if color_choice == 'b':
        best_move_found = best_move(board, depth, position_counts, transposition_table)
        if best_move_found is not None:
            print(f"Bot plays: {best_move_found}")
            board.push(best_move_found)
        else:
            print("Bot cannot find a valid move.")
        board_pieces = update_board_pieces(board)

    while not board.is_game_over():
        print_custom_board(board_colors, board_pieces, orientation)
        print(board)

        if board.can_claim_threefold_repetition():
            print("Draw by threefold repetition!")
            break

        try:
            player_move = os.getenv('PLAYER_MOVE', input("Enter your move in UCI format (e.g., e2e4): "))
        except EOFError:
            player_move = 'e2e4'
        move = chess.Move.from_uci(player_move)

        if chess.Move.from_uci(player_move).promotion is not None:
            promotion_piece = input("Promote to (q, r, b, n): ").strip().lower()
            while promotion_piece not in ['q', 'r', 'b', 'n']:
                promotion_piece = input("Invalid choice. Promote to (q, r, b, n): ").strip().lower()
            move = chess.Move.from_uci(player_move[:4] + promotion_piece)

        if move in board.legal_moves:
            board.push(move)
        else:
            print("Invalid move! Try again.")
            continue

        board_pieces = update_board_pieces(board)

        best_move_found = best_move(board, depth, position_counts, transposition_table)
        if best_move_found is not None:
            print(f"Bot plays: {best_move_found}")
            board.push(best_move_found)
        else:
            print("Bot cannot find a valid move.")
            break

        board_pieces = update_board_pieces(board)

    print_custom_board(board_colors, board_pieces, orientation)
    print(board)

    if board.is_checkmate():
        print("Checkmate! Game over.")
    elif board.is_stalemate():
        print("Stalemate! Game over.")
    elif board.is_insufficient_material():
        print("Draw by insufficient material.")
    elif board.can_claim_threefold_repetition():
        print("Draw by threefold repetition.")
    elif board.is_variant_draw():
        print("Draw by variant rules.")
    else:
        print("Game over.")
