"""
Creating Chess with Tkinter

Simplified with python-chess: https://python-chess.readthedocs.io/en/latest/#

- Using FEN for board tracking.
- Tkinter for GUI.

Created by Quentin Romero Lauro
"""
# TODO: image resizing based on board size
# Link with main 

import tkinter as tk
from tkinter.constants import NW
from PIL import ImageTk, Image
import chess

# create root window
root = tk.Tk()


class ChessBoard:
    
    # color 1 dark, color 2 light
    def __init__(self, parent, size, active, rows = 8, cols = 8, color1 = "#789658", color2 = "#eeeed3"):
        self.parent = parent        
        self.size = size
        self.active = active
        self.rows = rows
        self.cols = cols
        self.color1 = color1
        self.color2 = color2
        self.board = chess.Board()
        self.fen = self.board.fen()
        self.squares = {}
        self.pieces = {}
        self.prevClick = None
        self.selectedLegalMoves = []
        self.pieceImages = {}
        self.createImages()
        
        self.canvas = tk.Canvas(self.parent, height=size, width=size, borderwidth=0, bg="white")
        self.canvas.bind("<ButtonPress-1>", self.leftClick)
        self.canvas.bind("<ButtonRelease-1>", self.leftRelease)
        
        
    def createImages(self):
        for char in self.pieceImages:
            del self.pieceImages[char]
        
        imageConstant = 8
        self.pieceImages["k"] = ImageTk.PhotoImage((Image.open("chessPieces/blackKing.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["q"] = ImageTk.PhotoImage((Image.open("chessPieces/blackQueen.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["b"] = ImageTk.PhotoImage((Image.open("chessPieces/blackBishop.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["n"] = ImageTk.PhotoImage((Image.open("chessPieces/blackKnight.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["r"] = ImageTk.PhotoImage((Image.open("chessPieces/blackRook.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["p"] = ImageTk.PhotoImage((Image.open("chessPieces/blackPawn.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))

        self.pieceImages["K"] = ImageTk.PhotoImage((Image.open("chessPieces/whiteKing.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["Q"] = ImageTk.PhotoImage((Image.open("chessPieces/whiteQueen.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["B"] = ImageTk.PhotoImage((Image.open("chessPieces/whiteBishop.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["N"] =  ImageTk.PhotoImage((Image.open("chessPieces/whiteKnight.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["R"] = ImageTk.PhotoImage((Image.open("chessPieces/whiteRook.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        self.pieceImages["P"] = ImageTk.PhotoImage((Image.open("chessPieces/whitePawn.png").resize(((self.size//imageConstant), (self.size//imageConstant) ))).convert("RGBA"))
        
        
    def drawBoard(self):
        currColor = self.color1
        for row in range(self.rows):
            if currColor == self.color1:
                currColor = self.color2 
            else:
                currColor = self.color1
        
            for col in range(self.cols):
                squareSize = self.size//8
                x0 = squareSize * row
                y0 = squareSize * col
                x1 = x0 + squareSize
                y1 = y0 + squareSize
                
                # save the rectangle objects, so we can change their color when their position is pressed
                # save the color with it so we can revert it back to its old color if needed
                self.squares[(row, col)] = self.canvas.create_rectangle(x0, y0, x1, y1, fill=currColor), currColor
                
                self.canvas.create_text((x0+(squareSize//2)), (y0 + (squareSize//2)), text=f"{row}, {col}")
                
                if currColor == self.color1:
                    currColor = self.color2 
                else:
                    currColor = self.color1
    
        self.canvas.pack()
        self.placePieces(self.fen)

        
    def placePieces(self, fen):
        # places pieces based off fen format
        # yes, probably not most efficent, better done when iterating through to put the rectangles on to create the board
        row = 0
        col = 0
        squareSize = self.size//8
        for char in fen:
            if char.isalpha():
                x0 = squareSize * row
                y0 = squareSize * col
                self.pieces[(row, col)] = self.canvas.create_image(x0, y0, anchor=NW, image=self.pieceImages[char])
                row += 1
            elif char.isdigit():
                row += (int(char))
            elif char == " ":
                break
            if row > 7:
                row = 0
                col += 1    
        
    
    # gets which square is clicked based on size of board
    # check this is right
    def getSquareMatrix(self, x, y):
        # return square in row, col
        row = x // (self.size//8)
        col = y // (self.size//8)
        return row, col
    
    # returns square in notation
    # need to test
    def getSquareNotation(self, x, y):
        return self.convertToNotation(self.getSquareMatrix(x, y))
         
        
    # takes in position ex/ e4, and returns 4, 4
    def convertToMatrix(self, position):
        letters = "abcdefgh"
        return letters.index(position[0]), 8 - int(position[1])    
    
    
    def convertToNotation(self, matrixPosition):
        letters = "abcdefgh"
        return letters[matrixPosition[0]] + str(8-matrixPosition[1])
    
    # use python chess library to get legal moves 
    def getLegalPieceMoves(self, position):
        legalMoves = []
        # formats input
        if isinstance(position, tuple):
            piecePosition = self.convertToNotation(position)
        else:
            piecePosition = position
        
        for possibleMove in range(63):
            try:
                self.board.find_move(chess.SQUARE_NAMES.index(piecePosition), possibleMove)
                legalMoves.append(chess.SQUARE_NAMES[possibleMove])
            except:
                pass
        
        return legalMoves
      
    # takes in square in notation, returns True if it is a legal move based on previous click
    # checks if newSquare is a move for prevSquare
    def checkIfMove(self, prevSquare, newSquare):
        if prevSquare != None:
            legalMoves = self.getLegalPieceMoves(prevSquare)
            if newSquare in legalMoves:
                return True
            else:
                return False
        else:
            return False
    
    
    # checks if there is a piece in a particular square, input is notation
    def checkIfPiece(self, square):
        if self.board.piece_at(chess.parse_square(square)) != None:
            return True
        else:
            return False
        
    # White is True, Black is False
    # returns True for white and false for black
    def getPieceColor(self, square):
        return str(self.board.piece_at(chess.parse_square(square))).isupper()
    
    
    def getPiece(self, square):
        return str(self.board.piece_at(chess.parse_square(square)))
    
    
    def isCastle(self, prevPosition, newPosition):
        # if piece is king:
            # if piece is now more than one over, considering that this program only lets you make legal moves
        if self.getPiece(prevPosition).upper() == "K":
            if abs(self.convertToMatrix(prevPosition)[0] - self.convertToMatrix(newPosition)[0]) >= 2:
                return True
        else:
            return False

    
    
    
    def unhighlightAll(self):
        for position in self.squares:
            self.canvas.itemconfig(self.squares[position][0], fill=self.squares[position][1])
    
    
    def highlightLegalMoves(self, square):
        legalMoves = self.getLegalPieceMoves(square)
        for move in legalMoves:
            matrixPosition = self.convertToMatrix(move)
            self.canvas.itemconfig(self.squares[matrixPosition][0], fill="lightgreen")
    
    # newSquare is the location of the newest click
    # needs to be tested
    def highlightSquaresAccordingly(self, prevSquare, newSquare):
        # if it is not a move and is not a piece, based on prevSquare selected
            # if it has a piece, and it is that side's turn: highlight piece square and legal moves
        # else: unhighlightall squares
        #     if it is a move make the move
        isMove = self.checkIfMove(prevSquare, newSquare)
        isPiece = self.checkIfPiece(newSquare)
        newSquareInMatrix = self.convertToMatrix(newSquare)
        if isMove == False and isPiece == True and (self.getPieceColor(newSquare) == self.board.turn): 
            # unhighlight all squares
            self.unhighlightAll()
            # highlight the piece and it's legal moves
            self.canvas.itemconfig(self.squares[newSquareInMatrix][0], fill="green")
            self.highlightLegalMoves(newSquare)
        else:
            self.unhighlightAll()

    def logMove(self, previousPosition, newPosition):
        uciMove = previousPosition + newPosition
        self.board.push(chess.Move.from_uci(uciMove))
       
    
    def castleOnBoard(self, previousPosition, newPosition):
        newPositionMatrix = self.convertToMatrix(newPosition)
        previousPositionMatrix = self.convertToMatrix(previousPosition)
        piece = self.getPiece(previousPosition) # gets king piece
        
        # determine color of piece
        if self.board.turn:
            # white
            pieceCol = 7
            rookPiece = "R"
        else:
            # black
            pieceCol = 0 
            rookPiece = "r"
            
        if newPositionMatrix[0] > 4:
            # castle right
            newKingRow = 6
            newRookRow = 5
            oldRookRow = 7
                
        else:
            # castle left
            newKingRow = 2
            newRookRow = 3
            oldRookRow = 0
        
        # helper
        squareSize = self.size//8
        # delete, erase king
        self.canvas.delete(self.pieces[previousPositionMatrix])
        del self.pieces[previousPositionMatrix]
        
        # delete, erase rook
        self.canvas.delete(self.pieces[(oldRookRow, pieceCol)])
        del self.pieces[(oldRookRow, pieceCol)]
        # put new king and new rook
        x0 = squareSize * newKingRow
        y0 = squareSize * pieceCol
        x1 = squareSize * newRookRow
        # new king
        self.pieces[(newKingRow, pieceCol)] = self.canvas.create_image(x0, y0, anchor=NW, image=self.pieceImages[piece])
        # new rook
        self.pieces[(newRookRow, pieceCol)] = self.canvas.create_image(x1, y0, anchor=NW, image=self.pieceImages[rookPiece])

    
    
    # TODO: Fix castling
        
    def putMoveOnBoard(self, previousPosition, newPosition):
        # get the piece image object
        # update the objects coordinates to the new square's coordinates
        pieceObjectMatrixPosition = self.convertToMatrix(previousPosition)
        newPieceMatrixPosition = self.convertToMatrix(newPosition)
        pieceChar = str(self.board.piece_at(chess.parse_square(previousPosition)))
        
        # if there is a piece in the new position, it means a piece was taken, so delete that piece
        if newPieceMatrixPosition in self.pieces:
            self.canvas.delete(self.pieces[newPieceMatrixPosition])
            del self.pieces[newPieceMatrixPosition]
            
        # delete the image object
        self.canvas.delete(self.pieces[pieceObjectMatrixPosition])
        # delete old piece object from dictionary
        del self.pieces[pieceObjectMatrixPosition]
        squareSize = self.size//8
        x0 = squareSize * newPieceMatrixPosition[0]
        y0 = squareSize * newPieceMatrixPosition[1]
        # create new image object
        self.pieces[newPieceMatrixPosition] = self.canvas.create_image(x0, y0, anchor=NW, image=self.pieceImages[pieceChar])
        
        
    def updateOnFen(self, fen):
        for matrixPosition in self.pieces:
            self.canvas.delete(self.pieces[matrixPosition[0], matrixPosition[1]])
        self.fen = fen
        self.pieces.clear()
        self.placePieces(fen)
    
    
        
    # only makes the move if it is legal
    def makeMove(self, previousSquare, newSquare):
        if self.checkIfMove(previousSquare, newSquare):
            if self.isCastle(previousSquare, newSquare):
                self.castleOnBoard(previousSquare, newSquare)
            else:
                self.putMoveOnBoard(previousSquare, newSquare)
            self.logMove(previousSquare, newSquare)
    
     
    def leftClick(self, event):
        if self.active:
            clickX = event.x
            clickY = event.y
            if self.prevClick is not None:
                prevX = self.prevClick[0]
                prevY = self.prevClick[1]
                prevClickedSquareInNotation = self.getSquareNotation(prevX, prevY)
            else:
                prevClickedSquareInNotation = None
            clickedSquareInMatrix = self.getSquareMatrix(clickX, clickY)
            clickedSquareInNotation = self.getSquareNotation(clickX, clickY)
            
            # highlight squares as needed
            self.highlightSquaresAccordingly(prevClickedSquareInNotation, clickedSquareInNotation)
            # make moves as needed
            self.makeMove(prevClickedSquareInNotation, clickedSquareInNotation)
            
            self.prevClick = [clickX, clickY]
        
              
    # todo: add drag and drop feature 
    def leftRelease(self, event):
        
        return True
    
    
            
            


# TODO: make pieces adjust to size of board 
if __name__ == "__main__":
    board = ChessBoard(root, 500, True)
    board.drawBoard()
    #board.updateOnFen("rnbqkb1r/pppp1p1p/5n2/4p1p1/4P1P1/2N4B/PPPP1P1P/R1BQK1NR")
    root.mainloop()