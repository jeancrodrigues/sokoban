from maze import Maze
from state import State
from cardinal import *

class Problem:
    """Representação de um problema a ser resolvido por um algoritmo de busca clássica.
    A formulação do problema - instância desta classe - reside na 'mente' do agente."""


    def __init__(self):
        self.initialState = State(0,0,[],0)
        self.goalState = State(0,0,[],0)

    def createMaze(self, maxRows, maxColumns):
        """Este método instancia um labirinto - representa o que o agente crê ser o labirinto.
        As paredes devem ser colocadas fora desta classe porque este.
        @param maxRows: máximo de linhas do labirinto.
        @param maxColumns: máximo de colunas do labirinto."""
        self.mazeBelief = Maze(maxRows, maxColumns)
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.cost = [[0.0 for j in range(maxRows*maxColumns)]for i in range(8)]

    def defInitialState(self, row, col, boxes):
        """Define o estado inicial.
        @param row: linha do estado inicial.
        @param col: coluna do estado inicial."""
        self.initialState.row = row
        self.initialState.col = col
        self.initialState.boxes = boxes

    def defGoalState(self, row, col, boxes):
        """Define o estado objetivo.
        @param row: linha do estado objetivo.
        @param col: coluna do estado objetivo."""
        self.goalState.row = row
        self.goalState.col = col
        self.goalState.boxes = boxes

    def suc(self, state, action):
        """Função sucessora: recebe um estado e calcula o estado sucessor ao executar uma ação.
        @param state: estado atual.
        @param action: ação a ser realizado a partir do estado state.
        @return estado sucessor"""
        row = state.row
        col = state.col

        # Incrementa a linha e coluna de acordo com a respectiva ação
        # rowIncrement e colIncrement estão definidos em cardinal.py
        row += rowIncrement[action] 
        col += colIncrement[action]

        # Verifica limites
        if row < 0:
            row = 0
        if col < 0:
            col = 0
        if row == self.mazeBelief.maxRows:
            row = self.mazeBelief.maxRows - 1
        if col == self.mazeBelief.maxColumns:
            col = self.mazeBelief.maxColumns - 1
        
        # Se tiver parede agente fica na posição original
        if self.mazeBelief.walls[row][col] == 1: 
            row = state.row
            col = state.col

        boxes = []
        for box in state.boxes:
            boxes.append((box[0],box[1]))

        # verifica caixa e se pode empurrar
        if ( row, col ) in boxes :
            rowBox = row + rowIncrement[action]
            colBox = col + colIncrement[action]
            if rowBox < 0 or colBox < 0 or rowBox > self.mazeBelief.maxRows - 1 or colBox > self.mazeBelief.maxColumns -1 or self.mazeBelief.walls[rowBox][colBox] == 1:
                return State( state.row, state.col, boxes , state.cost + 1)
            else:
                boxes.remove((row,col))
                boxes.append((rowBox, colBox))
        
        return State(row, col, boxes, state.cost + 1)

    def possibleActions(self, state):
        """Retorna as ações possíveis de serem executadas em um estado, desconsiderando movimentos na diagonal.
        O valor retornado é um vetor de inteiros.
        Se o valor da posição é -1 então a ação correspondente não pode ser executada, caso contrário valerá 1.
        Exemplo: se retornar [1, -1, -1, -1] apenas a ação 0 pode ser executada, ou seja, apena N.
        @param state: estado atual.
        @return ações possíveis"""
        
        actions = [1,1,1,1] # Supõe que todas as ações (vertical e horizontal) são possíveis

        # @TODO: Implementação do aluno

        row = state.row
        col = state.col 

        # Esta no limite superior, não pode ir para N
        if row == 0: 
            actions[N] = -1
        # Esta no limite direito, não pode ir para L
        if col == self.mazeBelief.maxColumns - 1:
            actions[L] = -1
        # Esta no limite inferior, não pode ir para S
        if row == self.mazeBelief.maxRows - 1:
            actions[S]= -1
        # Esta no limite esquerdo, não pode ir para O
        if col == 0:
            actions[O] = -1

        walls = self.mazeBelief.walls
        # Testa se há parede nas direções
        if actions[N] != -1 and walls[row - 1][col] == 1: # Norte
            actions[N] = -1
        if actions[L] != -1 and walls[row][col + 1] == 1: # Leste
            actions[L] = -1
        if actions[S] != -1 and walls[row + 1][col] == 1: # Sul
            actions[S] = -1
        if actions[O] != -1 and walls[row ][col - 1] == 1: # Oeste
            actions[O] = -1

        # Testa se há caixas nas direções ( caixa e limite ) , ( caixa e parede ), ( caixa e caixa )
        boxes = state.boxes

        if actions[N] != -1:
            boxNminus1 = any( [ ( row - 1 , col ) == box for box in boxes ] )
            boxNminus2 = any( [ ( row - 2 , col ) == box for box in boxes ] )
            limitNminus2 = row - 2 < 0
            wallNminus2 = row - 2 >= 0 and walls[row - 2][col] == 1

            if ( boxNminus1 and limitNminus2 ) or ( boxNminus1 and wallNminus2 ) or ( boxNminus1 and boxNminus2 ): # Norte
                actions[N] = -1

        if actions[L] != -1 : 
            boxLplus1 = any( [ ( row , col + 1 ) == box for box in boxes ] )
            boxLplus2 = any( [ ( row , col + 2 ) == box for box in boxes ] )
            limitLplus2 = col + 2 > self.mazeBelief.maxColumns - 1
            wallLplus2 = col + 2 <= self.mazeBelief.maxColumns - 1 and walls[row][col+2] == 1

            if ( boxLplus1 and limitLplus2 ) or ( boxLplus1 and wallLplus2 ) or ( boxLplus1 and boxLplus2 ): # Leste
                actions[L] = -1

        if actions[S] != -1 : 
            boxSplus1 = any( [ ( row + 1 , col ) == box for box in boxes ] )
            boxSplus2 = any( [ ( row + 2 , col ) == box for box in boxes ] )
            limitSplus2 = row + 2 > self.mazeBelief.maxRows - 1
            wallSplus2 = row + 2 <= self.mazeBelief.maxRows - 1 and walls[row + 2][col] == 1

            if ( boxSplus1 and limitSplus2 ) or ( boxSplus1 and wallSplus2 ) or ( boxSplus1 and boxSplus2 ): # Sul
                actions[S] = -1

        if actions[O] != -1 : 
            boxOminus1 = any( [ ( row , col - 1 ) == box for box in boxes ] )
            boxOminus2 = any( [ ( row , col - 2 ) == box for box in boxes ] )
            limitOminus2 = col - 2 < 0
            wallOminus2 = col - 2 >= 0 and walls[row][col-2] == 1

            if ( boxOminus1 and limitOminus2 ) or ( boxOminus1 and wallOminus2 ) or ( boxOminus1 and boxOminus2 ): # Oeste
                actions[O] = -1

        return actions

    def isBlockAction(self, state): # testa se alguma caixa está em um canto da parede ou limite
        walls = self.mazeBelief.walls
        blocked = False
        for box in state.boxes:
            if box in self.goalState.boxes: # permite bloquear se for objetivo
                return False
            if not blocked:
                if box[0] == 0 or box[0] == self.mazeBelief.maxRows - 1:
                    if box[1] == 0 or box[1] == self.mazeBelief.maxColumns - 1 :
                        blocked = True
                    elif walls[box[0]][box[1]-1] == 1 or  walls[box[0]][box[1]+1] == 1:
                        blocked = True
                    else:
                        blocked = not any( [ gbox[0] == box[0] for gbox in self.goalState.boxes ] )
                elif box[1] == 0 or box[1] == self.mazeBelief.maxColumns - 1:
                    if walls[box[0]-1][box[1]] == 1 or  walls[box[0]+1][box[1]] == 1:
                        blocked = True
                    else:
                        blocked = not any( [ gbox[1] == box[1] for gbox in self.goalState.boxes ] )
        return blocked
    
    def checkWall(self, sbox, dbox):
        walls = self.mazeBelief.walls
        wall = False
        srow = min([sbox[0], dbox[0]])
        drow = max([sbox[0], dbox[0]])
        scol = min([sbox[1], dbox[1]])
        dcol = max([sbox[1], dbox[1]])        
        if srow == drow:
            wall += 2 if any([ walls[srow][i] for i in range(scol,dcol+1) ]) else 0
                            
        if scol:
            wall += 2 if any( [ walls[i][scol] for i in range(srow, drow + 1) ] ) else 0
        return wall 

    def getActionCost(self, action):
        """Retorna o custo da ação.
        @param action:
        @return custo da ação"""
        if (action == N or action == L or action == O or action == S):
            return 1.0

    def goalTest(self, currentState):
        """Testa se alcançou o estado objetivo.
        @param currentState: estado atual.
        @return True se o estado atual for igual ao estado objetivo."""
        return currentState == self.goalState # Operador de igualdade definido em __eq__ no arquivo state.py
