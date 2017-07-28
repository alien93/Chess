import model
import numpy as np
import chess
import chess.uci
import datetime
import time
from keras.models import load_model

class ReinforcementLearning(object):
    
    def __init__(self):
        self.model = model.build_model()
        self.handler = chess.uci.InfoHandler()
        self.engine = chess.uci.popen_engine('stockfish')
        self.engine.info_handlers.append(self.handler)

    def train_stockfish(self,board_state):
        input = self.fen_to_binary(board_state)

        board = chess.Board(board_state)
        self.engine.position(board)

        inputs = []
        outputs = []
        for move in board.legal_moves:
            inputs.append(self.fen_to_binary(board.fen(move)))
            self.engine.go(searchmoves = [move], movetime=200)
            outputs.append(round(self.handler.info['score'][1].cp/100.0,2))

        #reward_value = np.array([reward_value])
        self.model.fit(inputs, outputs, epochs=1, verbose=1)
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S') 
        self.model.save("models/" + timestamp)
        self.return_move(board_state)

    def train_heuristic(self,move, board_state, reward_value):
        input = np.array(self.fen_to_binary(board_state)).reshape((-1,256))
        reward_value = np.array([reward_value])
        self.model.fit(input, reward_value, epochs=1, verbose=1)
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S') 
        self.model.save("models/" + timestamp)
        self.return_move(board_state)

    def load_model(self,filepath):
        self.model = load_model(filepath)
        
    def return_move(self, board_state):
        board = chess.Board(board_state)
        inputs = []
        moves = []
        for move in board.legal_moves:
            moves.append(str(move))
            inputs.append(self.fen_to_binary(board.fen(move)))
        predicted = self.model.predict(inputs, verbose=1)
        print ("Predicted: ", predicted)
        max_predicted_idx = np.argmax(predicted)
        best_move = moves[max_predicted_idx]
        return best_move


    def fen_to_binary(self, board_state):
        fen = board_state.split(' ')[0].split('/')
        input = ""
        decoder = {
            'r':'0001',
            'n':'0010',
            'b':'0011',
            'q':'0100',
            'k':'0101',
            'p':'0110',

            'R':'0111',
            'N':'1000',
            'B':'1001',
            'Q':'1010',
            'K':'1011',
            'P':'1100'
        }
        for token in fen:
            letters = list(token)
            for letter in letters:
                if letter in decoder.keys():
                    input += decoder[letter]
                else:
                    no_of_empty_tiles = int (letter)
                    input += '0000'*no_of_empty_tiles
        input = [int(s) for s in list(input)]
        return input