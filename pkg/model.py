from view import View
from maze import Maze
from cardinal import *

class Model:
    """Model implementa um ambiente na forma de um labirinto com paredes e com um agente.
     A indexação da posição do agente é feita sempre por um par ordenado (lin, col). Ver classe Labirinto."""

    def __init__(self, rows, columns):
        """Construtor de modelo do ambiente físico (labirinto)
        @param rows: número de linhas do labirinto
        @param columns: número de colunas do labirinto
        """
        if rows <= 0:
            rows = 5
        if columns <= 0:
            columns = 5

        self.rows = rows
        self.columns = columns

        self.agentPos = [0,0]
        self.goalPos = []

        self.boxes = [[0 for j in range(columns)] for i in range(rows)]
        self.boxPos = []
        self.view = View(self)
        self.maze = Maze(rows,columns)

    def draw(self):
        """Desenha o labirinto em formato texto."""
        self.view.draw()

    def setAgentPos(self, row, col):
        """Utilizada para colocar o agente na posição inicial.
        @param row: a linha onde o agente será situado.
        @param col: a coluna onde o agente será situado.
        @return 1 se o posicionamento é possível, -1 se não for."""
        if (col < 0 or row < 0):
            return -1
        if (col >= self.maze.maxColumns or row >= self.maze.maxRows):
            return -1
        
        if self.maze.walls[row][col] == 1:
            return -1

        self.agentPos[0] = row
        self.agentPos[1] = col
        return 1
    
    def addGoalPos(self, row, col):
        """Utilizada para colocar o objetivo na posição inicial.
        @param row: a linha onde o objetivo será situado.
        @param col: a coluna onde o objetivo será situado.
        @return 1 se o posicionamento é possível, -1 se não for."""
        if (col < 0 or row < 0):
            return -1
        if (col >= self.maze.maxColumns or row >= self.maze.maxRows):
            return -1
        
        if self.maze.walls[row][col] == 1:
            return -1

        self.goalPos.append( ( row, col ) )
        return 1

    def addBoxPos(self, row, col):
        self.boxes[row][col] = 1
        self.boxPos.append((row, col))

    def go(self, direction):
        """Coloca o agente na posição solicitada pela ação go, desde que seja possível.
        Não pode ultrapassar os limites do labirinto nem estar em uma parede.
        @param direciton: inteiro de 0 a 7 representado as coordenadas conforme definido em cardinal.py"""
        row = self.agentPos[0]
        col = self.agentPos[1]

        if direction == N:
            row -= 1
        if direction == L:
            col += 1
        if direction == S:
            row += 1
        if direction == O:
            col -= 1

        # Verifica se está fora do grid
        if col < 0 or col >= self.maze.maxColumns:
            row = self.agentPos[0]
            col = self.agentPos[1]
        if row < 0 or row >= self.maze.maxRows:
            row = self.agentPos[0]
            col = self.agentPos[1]

        # Verifica se bateu em algum obstáculo
        if self.maze.walls[row][col] == 1:
            row = self.agentPos[0]
            col = self.agentPos[1]

        # Verifica se empurrou alguma caixa
        if self.boxes[row][col] == 1:
            boxRow = row
            boxCol = col

            if direction == N:
                boxRow -= 1
            if direction == L:
                boxCol += 1
            if direction == S:
                boxRow += 1
            if direction == O:
                boxCol -= 1

             # Verifica se está fora do grid
            if boxCol < 0 or boxCol >= self.maze.maxColumns:
                row = self.agentPos[0]
                col = self.agentPos[1]
            elif row < 0 or row >= self.maze.maxRows:
                row = self.agentPos[0]
                col = self.agentPos[1]
            elif self.boxes[boxRow][boxCol] == 1 or  self.maze.walls[boxRow][boxCol] == 1:: # verifica se tem outra caixa na sequencia ou parede
                row = self.agentPos[0]
                col = self.agentPos[1]
            else:
                self.boxes[row][col] = 0
                self.boxes[boxRow][boxCol] = 1
                self.boxPos.remove((row, col))
                self.boxPos.append((boxRow, boxCol))

        self.setAgentPos(row, col)