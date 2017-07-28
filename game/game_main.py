# -*- coding: utf-8 -*-
from subprocess import call
from time import sleep
from game_obj import Game
from node import Node
import heuristics
import random
import time
import json
from reinforcement_learning import ReinforcementLearning
import random

# open JSON file to read cached oves
with open("./moves_cache.json", "r") as f:
    try:
        cache_moves = json.load(f)
        # if the file is empty the ValueError will be thrown
    except ValueError:
        cache_moves = {'even': {}, 'odd': {}}

even_moves = cache_moves['even']
odd_moves = cache_moves['odd']

NO_EPOCHS = 10

class Game_Engine():
    def __init__(self, board_state):
        self.game = Game(board_state)
        self.computer = AI(self.game, 5)
        self.rl = ReinforcementLearning()

    def print_starting_message(self):
        print("\033[94m\033[1m===================================================================")
        print ("\033[93m               ______________                     \n"
               "               __  ____/__  /_____________________\n"
               "               _  /    __  __ \  _ \_  ___/_  ___/\n"
               "               / /___  _  / / /  __/(__  )_(__  ) \n"
               "               \____/  /_/ /_/\___//____/ /____/  \n"
               "                                                  ")
        print("\033[94m===================================================================\033[0m\033[22m")

    def prompt_user(self):
        self.print_starting_message()
        print("\nWelcome! To play, enter a command, e.g. '\033[95me2e4\033[0m'. To quit, type '\033[91mff\033[0m'.")
        self.computer.print_board(str(self.game))
        try:
            while self.game.status < 2:
                user_move = raw_input("\nMake a move: \033[95m")
                print("\033[0m")
                while user_move not in self.game.get_moves() and user_move != "ff":
                    user_move = raw_input("Please enter a valid move: ")
                if user_move == "ff":
                    print("You surrendered.")
                    break;
                self.game.apply_move(user_move)
                captured = self.captured_pieces(str(self.game))
                start_time = time.time()
                self.computer.print_board(str(self.game), captured)
                print("\nCalculating...\n")
                if self.game.status < 2:
                    current_state = str(self.game)
                    computer_move = self.rl.return_move(current_state)
                    PIECE_NAME = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
                    start = computer_move[:2]
                    end = computer_move[2:4]
                    piece = PIECE_NAME[self.game.board.get_piece(self.game.xy2i(computer_move[:2]))]
                    captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
                    if captured_piece != " ":
                        captured_piece = PIECE_NAME[captured_piece.lower()]
                        print("---------------------------------")
                        print("Computer's \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m at \033[91m{end}\033[0m.").format(piece = piece, start = start, captured_piece = captured_piece, end = end)
                        print("---------------------------------")
                    else:
                        print("---------------------------------")
                        print("Computer moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(piece = piece, start = start, end = end))
                        print("---------------------------------")
                    print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer.node_count))
                    print("\033[1mNodes cached:\033[0m         \033[93m{}\033[0m".format(len(self.computer.cache)))
                    print("\033[1mNodes found in cache:\033[0m \033[93m{}\033[0m".format(self.computer.found_in_cache))
                    print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
                    self.game.apply_move(computer_move)
                captured = self.captured_pieces(str(self.game))
                self.computer.print_board(str(self.game), captured)
            user_move = raw_input("Game over. Play again? y/n: ")
            if user_move.lower() == "y":
                self.game = Game()
                self.computer.game = self.game
                self.prompt_user()
            # cache moves into JSON file
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
        except KeyboardInterrupt:
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
            print("\nYou quitter!")

    # def write_to_cache(self):

    def train_heuristic(self):
        '''
        Computer plays against itself. Stockfish is the mentor
        '''
        self.print_starting_message()
        print("\nWelcome! This is a training mode. Computer will play against itself.")
        self.computer.print_board(str(self.game))
        try:
            while self.game.status < 2:

                # possible_moves = self.game.get_moves()
                # print ("Possible moves:" , possible_moves)
                current_state = str(self.game)
                user_move = self.rl.return_move(current_state) # possible_moves[random.randint(0, len(possible_moves)-1)]
                self.game.apply_move(user_move)

                # train
                # current_state = str(self.game)
                self.rl.train_heuristic(user_move, current_state, self.computer.get_heuristic(current_state))

                captured = self.captured_pieces(str(self.game))
                start_time = time.time()
                self.computer.print_board(str(self.game), captured)
                print("\nCalculating...\n")
                if self.game.status < 2:
                    current_state = str(self.game)

                    # possible_moves = self.game.get_moves()
                    # print ("Possible moves:" , possible_moves)
                    computer_move = self.rl.return_move(current_state) # possible_moves[random.randint(0, len(possible_moves)-1)]
                    
                    PIECE_NAME = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
                    start = computer_move[:2]
                    end = computer_move[2:4]
                    piece = PIECE_NAME[self.game.board.get_piece(self.game.xy2i(computer_move[:2]))]
                    captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
                    if captured_piece != " ":
                        captured_piece = PIECE_NAME[captured_piece.lower()]
                        print("---------------------------------")
                        print("Computer's \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m at \033[91m{end}\033[0m.").format(piece = piece, start = start, captured_piece = captured_piece, end = end)
                        print("---------------------------------")
                    else:
                        print("---------------------------------")
                        print("Computer moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(piece = piece, start = start, end = end))
                        print("---------------------------------")
                    print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer.node_count))
                    print("\033[1mNodes cached:\033[0m         \033[93m{}\033[0m".format(len(self.computer.cache)))
                    print("\033[1mNodes found in cache:\033[0m \033[93m{}\033[0m".format(self.computer.found_in_cache))
                    print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
                    self.game.apply_move(computer_move)

                    # train
                    current_state = str(self.game)
                    self.rl.train_heuristic(computer_move, current_state, self.computer.get_heuristic(current_state))

                captured = self.captured_pieces(str(self.game))
                self.computer.print_board(str(self.game), captured)
            user_move = raw_input("Training is complete. Train again? y/n: ")
            if user_move.lower() == "y":
                self.game = Game()
                self.computer.game = self.game
                self.train_heuristic()
            # cache moves into JSON file
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
        except KeyboardInterrupt:
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
            print("\nTraining was interrupted. The last network configuration is saved.")



    def train_stockfish(self):
        '''
        Computer plays against itself. Stockfish is the mentor
        '''
        self.print_starting_message()
        print("\nWelcome! This is a training mode. Computer will play against itself.")
        self.computer.print_board(str(self.game))
        try:
            while self.game.status < 2:

                # possible_moves = self.game.get_moves()
                # print ("Possible moves:" , possible_moves)
                current_state = str(self.game)
                user_move = self.rl.return_move(current_state) # possible_moves[random.randint(0, len(possible_moves)-1)]
                self.game.apply_move(user_move)

                # train
                # current_state = str(self.game)
                self.rl.train_stockfish(current_state)

                captured = self.captured_pieces(str(self.game))
                start_time = time.time()
                self.computer.print_board(str(self.game), captured)
                print("\nCalculating...\n")
                if self.game.status < 2:
                    current_state = str(self.game)

                    # possible_moves = self.game.get_moves()
                    # print ("Possible moves:" , possible_moves)
                    computer_move = self.rl.return_move(current_state) # possible_moves[random.randint(0, len(possible_moves)-1)]
                    
                    PIECE_NAME = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
                    start = computer_move[:2]
                    end = computer_move[2:4]
                    piece = PIECE_NAME[self.game.board.get_piece(self.game.xy2i(computer_move[:2]))]
                    captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
                    if captured_piece != " ":
                        captured_piece = PIECE_NAME[captured_piece.lower()]
                        print("---------------------------------")
                        print("Computer's \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m at \033[91m{end}\033[0m.").format(piece = piece, start = start, captured_piece = captured_piece, end = end)
                        print("---------------------------------")
                    else:
                        print("---------------------------------")
                        print("Computer moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(piece = piece, start = start, end = end))
                        print("---------------------------------")
                    print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer.node_count))
                    print("\033[1mNodes cached:\033[0m         \033[93m{}\033[0m".format(len(self.computer.cache)))
                    print("\033[1mNodes found in cache:\033[0m \033[93m{}\033[0m".format(self.computer.found_in_cache))
                    print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
                    self.game.apply_move(computer_move)

                    # train
                    current_state = str(self.game)
                    self.rl.train_stockfish(current_state)

                captured = self.captured_pieces(str(self.game))
                self.computer.print_board(str(self.game), captured)
            user_move = raw_input("Training is complete. Train again? y/n: ")
            if user_move.lower() == "y":
                self.game = Game()
                self.computer.game = self.game
                self.train_stockfish()
            # cache moves into JSON file
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
        except KeyboardInterrupt:
            with open("./moves_cache.json", "w") as f:
                if self.computer.max_depth % 2 == 0:
                    for key in self.computer.cache:
                        cache_moves["even"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
                else:
                    for key in self.computer.cache:
                        cache_moves["odd"][key] = self.computer.cache[key]
                    json.dump(cache_moves, f)
            print("\nTraining was interrupted. The last network configuration is saved.")


    def captured_pieces(self, board_state):
        piece_tracker = {'P': 8, 'B': 2, 'N': 2, 'R': 2, 'Q': 1, 'K': 1, 'p': 8, 'b': 2, 'n': 2, 'r': 2, 'q': 1, 'k': 1}
        captured = {
            "w": [],
            "b": []
        }
        for char in board_state.split()[0]:
            if char in piece_tracker:
                piece_tracker[char] -= 1
        for piece in piece_tracker:
            if piece_tracker[piece] > 0:
                if piece.isupper():
                    captured['w'] += piece_tracker[piece] * piece
                else:
                    captured['b'] += piece_tracker[piece] * piece
            piece_tracker[piece] = 0
        return captured

class AI():
    def __init__(self, game, max_depth=4, node_count=0):
        self.max_depth = max_depth
        self.game = game
        self.node_count = node_count
        if self.max_depth % 2 == 0:
            self.cache = cache_moves['even']
        else:
            self.cache = cache_moves['odd']
        self.found_in_cache = 0

    def print_board(self, board_state, captured={"w": [], "b": []}):
        PIECE_SYMBOLS = {'P': '♟',
                        'B': '♝',
                        'N': '♞',
                        'R': '♜',
                        'Q': '♛',
                        'K': '♚',
                        'p': '\033[36m\033[1m♙\033[0m',
                        'b': '\033[36m\033[1m♗\033[0m',
                        'n': '\033[36m\033[1m♘\033[0m',
                        'r': '\033[36m\033[1m♖\033[0m',
                        'q': '\033[36m\033[1m♕\033[0m',
                        'k': '\033[36m\033[1m♔\033[0m'}
        board_state = board_state.split()[0].split("/")
        board_state_str = "\n"
        white_captured = " ".join(PIECE_SYMBOLS[piece] for piece in captured['w'])
        black_captured = " ".join(PIECE_SYMBOLS[piece] for piece in captured['b'])
        for i, row in enumerate(board_state):
            board_state_str += str(8-i)
            for char in row:
                if char.isdigit():
                    board_state_str += " ♢" * int(char)
                else:
                    board_state_str += " " + PIECE_SYMBOLS[char]
            if i == 0:
                board_state_str += "   Captured:" if len(white_captured) > 0 else ""
            if i == 1:
                board_state_str += "   " + white_captured
            if i == 6:
                board_state_str += "   Captured:" if len(black_captured) > 0 else ""
            if i == 7:
                board_state_str += "   " + black_captured
            board_state_str += "\n"
        board_state_str += "  A B C D E F G H"
        self.found_in_cache = 0
        self.node_count = 0
        print(board_state_str)

    def get_moves(self, board_state=None):
        print ("get_moves is used")
        if board_state == None:
            board_state = str(self.game)
        possible_moves = []
        for move in Game(board_state).get_moves():
            if (len(move) < 5 or move[4] == "q"):
                clone = Game(board_state)
                clone.apply_move(move)
                node = Node(str(clone))
                node.algebraic_move = move
                possible_moves.append(node)
        return possible_moves

    def get_heuristic(self, board_state=None):
        cache_parse = board_state.split(" ")[0] + " " + board_state.split(" ")[1]
        if board_state == None:
            board_state = str(self.game)
        if cache_parse in self.cache:
            self.found_in_cache += 1
            return self.cache[cache_parse]
        clone = Game(board_state)
        total_points = 0
        # total piece count
        total_points += heuristics.material(board_state, 100)
        total_points += heuristics.piece_moves(clone, 50)
        total_points += heuristics.in_check(clone, 1)
        total_points += heuristics.pawn_structure(board_state, 1)
        self.cache[cache_parse] = total_points
        return total_points

if __name__ == '__main__':
    new_test = Game_Engine('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    # new_test.rl.load_model("models/2017-07-28-12-02-07")
    # new_test.prompt_user()
    new_test.train_stockfish()
    # new_test.train_heuristic()
