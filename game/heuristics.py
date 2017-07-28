from game_obj import Game

def material(board_state, weight):
    black_points = 0
    board_state = board_state.split()[0]
    piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 0}
    for piece in board_state:
        if piece.islower():
            black_points += piece_values[piece]
        elif piece.isupper():
            black_points -= piece_values[piece.lower()]
    return black_points * weight

def piece_moves(game, weight):
    black_points = 0
    turn = str(game).split()[1]
    square_values = {"e4": 1, "e5": 1, "d4": 1, "d5": 1, "c6": 0.5, "d6": 0.5, "e6": 0.5, "f6": 0.5,
                    "c3": 0.5, "d3": 0.5, "e3": 0.5, "f3": 0.5, "c4": 0.5, "c5": 0.5, "f4": 0.5, "f5": 0.5}
    possible_moves = game.get_moves()
    for move in possible_moves:
        if turn == "b":
            if move[2:4] in square_values:
                black_points += square_values[move[2:4]]
        else:
            if move[2:4] in square_values:
                black_points -= square_values[move[2:4]]
    return black_points

def pawn_structure(board_state, weight):
    black_points = 0
    board_state, current_player = [segment for segment in board_state.split()[:2]]
    board_state = board_state.split("/")

    # convert fen into matrix:
    board_state_arr = []
    for row in board_state:
    	row_arr = []
    	for char in row:
    		if char.isdigit():
    			for i in range(int(char)):
    				row_arr.append(" ")
    		else:
    			row_arr.append(char)
    	board_state_arr.append(row_arr)

    # determine pawn to search for based on whose turn it is
    for i, row in enumerate(board_state_arr):
        for j in range(len(row)):
            if board_state_arr[i][j] == "p":
                tl = i-1, j-1
                tr = i-1, j+1
                if tl[0] >= 0 and tl[0] <= 7 and tl[1] >= 0 and tl[1] <= 7:
                    if board_state_arr[tl[0]][tl[1]] == "p":
                        black_points += 1
                if tr[0] >= 0 and tr[0] <= 7 and tr[1] >= 0 and tr[1] <= 7:
                    if board_state_arr[tr[0]][tr[1]] == "p":
                        black_points += 1
    return black_points * weight

def in_check(game, weight):
    black_points = 0
    current_status = game.status
    # Turn should be 'w' or 'b'
    turn = str(game).split(" ")[1]
    # Check or Checkmate situations
    if turn == "w":
        if current_status == 1:
            black_points += 1 * weight
        elif current_status == 2:
            black_points += float("inf")
    else:
        if current_status == 1:
            black_points -= 1 * weight
        elif current_status == 2:
            black_points += float("-inf")
    return black_points