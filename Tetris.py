#################################################
# hw7.py: Tetris!
#
# Your name: Xiqiao Guo
# Your andrew id: xiqiaog
#
# Your partner's name: Shenyi Xie
# Your partner's andrew id: shenyix
#################################################

import cs112_f19_week7_linter
import math, copy, random

from cmu_112_graphics import *
from tkinter import *

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#################################################
# Functions for you to write
#################################################

# get the size information to make the board
def gameDimensions():
    rows = 15
    cols = 10
    cellSize = 20
    margin = 25
    return (rows, cols, cellSize, margin)

# initiate our model 
def appStarted(app):
    (rows, cols, cellSize, margin) = gameDimensions()
    app.rows = rows
    app.cols = cols
    app.cellSize = cellSize
    app.margin = margin
    app.emptyColor = "blue"

    iPiece = [
        [  True,  True,  True,  True ]
    ]
    jPiece = [
        [  True, False, False ],
        [  True,  True,  True ]
    ]
    lPiece = [
        [ False, False,  True ],
        [  True,  True,  True ]
    ]
    oPiece = [
        [  True,  True ],
        [  True,  True ]
    ]
    sPiece = [
        [ False,  True,  True ],
        [  True,  True, False ]
    ]
    tPiece = [
        [ False,  True, False ],
        [  True,  True,  True ]
    ]
    zPiece = [
        [  True,  True, False ],
        [ False,  True,  True ]
    ]
    app.tetrisPieces = [ iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, 
                         zPiece ]
    app.tetrisPieceColors = [ "red", "yellow", "magenta", "pink", "cyan", 
                              "green", "orange" ]
    reStart(app)

# reset the gamesetting when a new game starts
def reStart(app):
    app.rotateChange = False
    app.countGame = 0
    app.timerDelay = 500
    app.board = [app.cols*[app.emptyColor] for row in range(app.rows)]
    app.fallingPiece = None
    app.fallingPieceColor = None
    app.isGameOver = False
    app.isSpeed = False
    app.score = 0
    newFallingPiece(app)

# choose a random piece of random color
def newFallingPiece(app):
    randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
    app.fallingPiece = app.tetrisPieces[randomIndex]
    app.fallingPieceColor = app.tetrisPieceColors[randomIndex]
    app.pieceTop = 0
    app.pieceLeft = (app.cols//2)-(len(app.fallingPiece[0])//2)

# modelToView
def getCellBounds(app, row, col):
    x0 = app.margin + col*app.cellSize
    y0 = app.margin + row*app.cellSize
    x1 = x0+app.cellSize
    y1 = y0+app.cellSize
    return (x0, y0, x1, y1)

# Control the flow of the game
def timerFired(app):
    if not app.isGameOver:
        if not moveFallingpiece(app, +1, 0):
            placeFallingPiece(app)
            newFallingPiece(app)
            app.isSpeed = False
            app.timerDelay = 800
            # end the game when no more piece can be put
            if not fallingPieceIsLegal(app):
                app.isGameOver = True 

# draw the piece into the board when it can no longer fall
def placeFallingPiece(app):
    fill = app.fallingPieceColor
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[0])):
            if app.fallingPiece[row][col]:
                # change the color of the board into the color of piece
                app.board[app.pieceTop+row][app.pieceLeft+col] = fill
    removeFullRows(app)

# remove the full rows from the board
def removeFullRows(app):
    fullRow = 0
    newBoard = []
    for row in range(len(app.board)):
        if app.emptyColor not in app.board[row]:    # full
            # track the rows removed 
            fullRow += 1
        else:   # not full
            newBoard.append(app.board[row])
    # fill the board with empty colors untill it's in the right size
    while len(newBoard) < app.rows:   
        newBoard.insert(0, [app.emptyColor]*app.cols)
    # update score when rows are removed
    app.score += fullRow**2
    app.board = newBoard

# trigger actions based on the operations of users
def keyPressed(app, event):
    if event.key == "r":
        reStart(app)
    if not app.isGameOver:
        if event.key == "Left":
            moveFallingpiece(app, 0, -1)
        elif event.key == "Right":
            moveFallingpiece(app, 0, +1)
        elif event.key == "Down":
            moveFallingpiece(app, +1, 0)
        # rotate counterclockwise
        elif event.key == "Up":
            app.rotateChange = False
            rotateFallingPiece(app)
        # rotate clockwise
        elif event.key == "c":
            app.rotateChange = True
            rotateFallingPiece(app)
        # hard drop
        elif event.key == "Space":
            app.isSpeed = True
            app.timerDelay = 0

# change the position of the piece as it falls down
def moveFallingpiece(app, drow, dcol):
    app.pieceTop += drow
    app.pieceLeft += dcol
    # withdraw the move if it's illegal
    if not fallingPieceIsLegal(app):
        app.pieceLeft -= dcol 
        app.pieceTop -= drow
        return False
    else: return True

# rotate the piece counterclockwise or clockwise 
def rotateFallingPiece(app):
    oldPiece = app.fallingPiece
    oldRows, oldCols = len(app.fallingPiece), len(app.fallingPiece[0])
    oldPieceTop, oldPieceLeft = app.pieceTop, app.pieceLeft
    newRows, newCols = oldCols, oldRows
    newPieceTop = oldPieceTop + oldRows//2 - newRows//2
    newPieceLeft = oldPieceLeft + oldCols//2 - newCols//2
    newPiece = [[None]*newCols for row in range(newRows)]
    for row in range(oldRows):
        for col in range(oldCols):
            # check direction of rotation
            if not app.rotateChange:    # rotate counterclockwise 
                newPiece[oldCols-1-col][row] = oldPiece[row][col]
            # rotate clockwise
            else: newPiece[col][oldRows-1-row] = oldPiece[row][col]
    app.fallingPiece = newPiece
    app.pieceTop, app.pieceLeft = newPieceTop, newPieceLeft
    # withdraw the move if the rotation is illegal
    if not fallingPieceIsLegal(app):
        app.fallingPiece = oldPiece
        app.pieceTop, app.pieceLeft = oldPieceTop, oldPieceLeft  

# check whether the move of the piece is allowed
def fallingPieceIsLegal(app):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[0])):
            if app.fallingPiece[row][col]:
                (newRow, newCol) = (row+app.pieceTop, col+app.pieceLeft)
                # stay in board
                if ((newRow < 0) or (newRow >= app.rows) or
                    (newCol < 0) or (newCol >= app.cols) or
                    # coincide with other pieces
                    (app.board[newRow][newCol] != app.emptyColor)):
                    return False
    return True

# draw the piece as it falls down
def drawFallingPiece(app, canvas):
    fill = app.fallingPieceColor
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[0])):
            if app.fallingPiece[row][col]:   
                # draw the piece by drawing its individual cell if exists.
                drawCell(app, canvas, app.pieceTop+row, app.pieceLeft+col, 
                         fill=fill)

# draw every cell of the board
def drawCell(app, canvas, row, col, fill):
    (x0, y0, x1, y1) = getCellBounds(app, row, col)
    canvas.create_rectangle(x0, y0, x1, y1, fill=fill, width=3)

# draw the background board of the game
def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            fill=app.board[row][col]
            drawCell(app, canvas, row, col, fill)

# print game over message when the game is over
def drawGameOver(app, canvas):
    if app.isGameOver:

        canvas.create_rectangle(app.margin, app.margin+app.cellSize, 
                                app.width-app.margin, 
                                app.margin+4*app.cellSize,
                                fill="black")
        canvas.create_text(app.width/2, app.margin+2*app.cellSize, 
                           fill="yellow", text="Game Over!", 
                           font="Arial 30 bold")

# show the score at the top of the board
def drawScore(app, canvas):
    canvas.create_text(app.width/2, app.margin/2, 
                       text=f"Score: {app.score}",
                       fill="blue", font="Arial 20 bold")

# draw the whole display of the game
def redrawAll(app, canvas):
    width = app.cols*app.cellSize+2*app.margin
    height = app.rows*app.cellSize+2*app.margin
    canvas.create_rectangle(0, 0, width, height, fill="orange")
    drawBoard(app, canvas)
    # if hard drop, hide the process of falling down
    if not app.isSpeed:
        drawFallingPiece(app, canvas)
    drawScore(app, canvas)
    drawGameOver(app, canvas)

# paly the game
def playTetris():
    (rows, cols, cellSize, margin) = gameDimensions()
    width = cols*cellSize+2*margin
    height = rows*cellSize+2*margin
    runApp(width=width, height=height)

#################################################
# main
#################################################

def main():
    cs112_f19_week7_linter.lint()
    playTetris()

if __name__ == '__main__':
    main()