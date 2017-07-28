import chess
import chess.uci

#Let's try our code with the starting position of chess:
fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
board = chess.Board(fen)
handler = chess.uci.InfoHandler()

#Now make sure you give the correct location for your stockfish engine file
#...in the line that follows: e.g., /home/.../stockfish_6_x64
engine = chess.uci.popen_engine('stockfish')

engine.info_handlers.append(handler)
engine.position(board)
if board.turn: print 'White to move'
else: print 'black to move'

for el in board.legal_moves:
    print el
    engine.go(searchmoves=[el],movetime=1000)
    print str(board.san(el)), 'eval = ', round(handler.info["score"][1].cp/100.0,2)