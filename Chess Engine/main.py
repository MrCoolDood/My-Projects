import os
import chess
import random

# Create a dictionary to represent the board with the default color assignments and pieces
board_colors = {}
board_pieces = {
    'a1': 'R1', 'b1': 'N1', 'c1': 'B1', 'd1': 'Q1', 'e1': 'K1', 'f1': 'B1', 'g1': 'N1', 
    'h1': 'R1',
    'a2': 'P1', 'b2': 'P1', 'c2': 'P1', 'd2': 'P1', 'e2': 'P1', 'f2': 'P1', 'g2': 'P1', 
    'h2': 'P1',
    'a7': 'p2', 'b7': 'p2', 'c7': 'p2', 'd7': 'p2', 'e7': 'p2', 'f7': 'p2', 'g7': 'p2', 
    'h7': 'p2',
    'a8': 'r2', 'b8': 'n2', 'c8': 'b2', 'd8': 'q2', 'e8': 'k2', 'f8': 'b2', 'g8': 'n2', 
    'h8': 'r2',
}

# Loop through all squares and assign default colors
for square in chess.SQUARES:
    if (chess.square_rank(square) + chess.square_file(square)) % 2 == 0:
        board_colors[square] = 'white'  # White square
    else:
        board_colors[square] = 'black'  # Black square

# Function to update board pieces based on the current state
def update_board_pieces(board):
    pieces = {}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            pieces[chess.square_name(square)] = piece.symbol()
    return pieces

# Function to print the board with custom colors, border lines, and pieces
def print_custom_board(board_colors, board_pieces, orientation):
    if orientation == 'black':
        ranks = range(8)
        files = range(7, -1, -1)
        file_labels = 'hg fe d c ba'
        rank_labels = '12345678'
    else:
        ranks = range(7, -1, -1)
        files = range(8)
        file_labels = 'ab c de f gh'
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

# Enhanced evaluation function with repetition penalty
def evaluate_board(board, position_counts):
    # Piece values
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # King is invaluable, but we still need to differentiate
    }

    # Calculate material balance
    material_score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                material_score += value
            else:
                material_score -= value

    # Penalize repeated positions
    board_fen = board.board_fen()
    repetition_penalty = position_counts.get(board_fen, 0) * 10  # Penalty increases with repetitions

    return material_score - repetition_penalty

# Minimax function with Alpha-Beta Pruning and Transposition Table
def minimax(board, depth, alpha, beta, maximizing_player, position_counts, 
            transposition_table):
    board_fen = board.board_fen()

    if board_fen in transposition_table:
        return transposition_table[board_fen]

    if depth == 0 or board.is_game_over():
        eval = evaluate_board(board, position_counts)
        transposition_table[board_fen] = eval
        return eval

    if maximizing_player:
        max_eval = -float('inf')
        for move in sorted(board.legal_moves, key=lambda m: 
                           m.uci()):  # Move ordering (simplified)
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False, position_counts, 
                           transposition_table)
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
            # Move ordering (simplified)
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True, position_counts, 
                           transposition_table)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[board_fen] = min_eval
        return min_eval

# Function to find the best move
def best_move(board, depth, position_counts, transposition_table):
    best_moves = []
    best_eval = -float('inf')
    for move in board.legal_moves:
        board.push(move)
        board_fen = board.board_fen()
        position_counts[board_fen] = position_counts.get(board_fen, 0) + 1
        move_eval = minimax(board, depth - 1, -float('inf'), float('inf'), 
                            False, position_counts, transposition_table)
        board.pop()
        position_counts[board_fen] -= 1
        if move_eval > best_eval:
            best_eval = move_eval
            best_moves = [move]
        elif move_eval == best_eval:
            best_moves.append(move)
    return random.choice(best_moves) if best_moves else None

# Initialize board
board = chess.Board()
depth = 5  # Set the desired depth
position_counts = {}  # Dictionary to count positions
transposition_table = {}  # Transposition table

# Use environment variables to get input values in a CI/CD environment
color_choice = os.getenv('COLOR_CHOICE', 'w')  # Default to 'w' if not set

# If running interactively, still ask for input
if os.getenv('GITHUB_ACTIONS') is None:  # Check if running in GitHub Actions
    color_choice = input("Do you want to play as white or black? (w/b): ").strip().lower()

# Validate input
while color_choice not in ['w', 'b']:
    color_choice = input("Invalid choice. Please enter 'w' for white or 'b' for black: ").strip().lower()

# Set the orientation based on the user's choice
orientation = 'black' if color_choice == 'b' else 'white'

# If the user chooses black, let the bot play first
if color_choice == 'b':
    best_move_found = best_move(board, depth, position_counts, transposition_table)
    if best_move_found is not None:
        print(f"Bot plays: {best_move_found}")
        board.push(best_move_found)
    else:
        print("Bot cannot find a valid move.")

# Update pieces for initial board
board_pieces = update_board_pieces(board)

# Play against the bot
while not board.is_game_over():
    print_custom_board(board_colors, board_pieces, orientation)  
    # Print the custom board with pieces
    print(board)  # Print the current board state

    # Check for threefold repetition
    if board.can_claim_threefold_repetition():
        print("Draw by threefold repetition!")
        break

    # Player's move
    player_move = input("Enter your move in UCI format (e.g., e2e4): ")
    move = chess.Move.from_uci(player_move)
    if move in board.legal_moves:
        board.push(move)
    else:
        print("Invalid move! Try again.")
        continue

    # Update board pieces based on current board state
    board_pieces = update_board_pieces(board)

    # Bot's move
    best_move_found = best_move(board, depth, position_counts, transposition_table)
    if best_move_found is not None:
        print(f"Bot plays: {best_move_found}")
        board.push(best_move_found)
    else:
        print("Bot cannot find a valid move.")
        break

    # Update board pieces based on current board state
    board_pieces = update_board_pieces(board)

# Print final board state
print_custom_board(board_colors, board_pieces, orientation)
print(board)

# End of the game messages
if board.is_checkmate():
    print("Checkmate! Game over.")
elif board.is_stalemate():
    print("Stalemate! Game over.")
elif board.is_insufficient_material():
    print("Draw by insufficient material.")
elif board.is_seventyfive_moves():
    print("Draw by seventy-five move rule.")
elif board.is_fivefold_repetition():
    print("Draw by fivefold repetition.")
elif board.is_variant_draw():
    print("Draw by variant rules.")
else:
    print("Game over.")
