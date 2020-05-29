from maze import Maze
from state import State
from cardinal import *

class Problem:
    """Representação de um problema a ser resolvido por um algoritmo de busca clássica.
    A formulação do problema - instância desta classe - reside na 'mente' do agente."""


    def __init__(self):
        self.initialState = State(0,0)
        self.goalState = State(0,0)

    def createMaze(self, maxRows, maxColumns):
        """Este método instancia um labirinto - representa o que o agente crê ser o labirinto.
        As paredes devem ser colocadas fora desta classe porque este.
        @param maxRows: máximo de linhas do labirinto.
        @param maxColumns: máximo de colunas do labirinto."""
        self.mazeBelief = Maze(maxRows, maxColumns)
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.cost = [[0.0 for j in range(maxRows*maxColumns)]for i in range(8)]

    def defInitialState(self, row, col):
        """Define o estado inicial.
        @param row: linha do estado inicial.
        @param col: coluna do estado inicial."""
        self.initialState.row = row
        self.initialState.col = col

    def defGoalState(self, row, col):
        """Define o estado objetivo.
        @param row: linha do estado objetivo.
        @param col: coluna do estado objetivo."""
        self.goalState.row = row
        self.goalState.col = col

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
        
        return State(row, col)

    def possibleActions(self, state):
        """Retorna as ações possíveis de serem executadas em um estado.
        O valor retornado é um vetor de inteiros.
        Se o valor da posição é -1 então a ação correspondente não pode ser executada, caso contrário valerá 1.
        Exemplo: se retornar [-1, -1, -1, 1, 1, -1, -1, -1] apenas as ações 3 e 4 podem ser executadas, ou seja, apenas SE e S.
        @param state: estado atual.
        @return ações possíveis"""
        
        actions = [1,1,1,1,1,1,1,1] # Supõe que todas as ações são possíveis
        
        # @TODO: Implementação do aluno
        
        row = state.row
        col = state.col 

        # Esta no limite superior, não pode ir para N, NE ou NO
        if row == 0: 
            actions[N] = actions[NE] = actions[NO] = -1
        # Esta no limite direito, não pode ir para NE, L ou SE
        if col == self.mazeBelief.maxColumns - 1:
            actions[NE] = actions[L] = actions[SE] = -1
        # Esta no limite inferior, não pode ir para SE, S ou SO
        if row == self.mazeBelief.maxRows - 1:
            actions[SE] = actions[S] = actions[SO] = -1
        # Esta no limite esquerdo, não pode ir para SO, O ou NO
        if col == 0:
            actions[SO] = actions[O] = actions[NO] = -1

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

        if actions[NE] != -1 and walls[row - 1][col + 1] == 1: # Nordeste
            actions[NE] = -1
        if actions[NO] != -1 and walls[row - 1][col - 1] == 1: # Noroeste
            actions[NO] = -1
        if actions[SE] != -1 and walls[row + 1][col + 1] == 1: # Sudeste
            actions[SE] = -1
        if actions[SO] != -1 and walls[row + 1][col - 1] == 1: # Sudoeste
            actions[SO] = -1

        return actions

    def possibleActionsWithoutCollaterals(self, state):
        """Retorna as ações possíveis de serem executadas em um estado, desconsiderando movimentos na diagonal.
        O valor retornado é um vetor de inteiros.
        Se o valor da posição é -1 então a ação correspondente não pode ser executada, caso contrário valerá 1.
        Exemplo: se retornar [1, -1, -1, -1, -1, -1, -1, -1] apenas a ação 0 pode ser executada, ou seja, apena N.
        @param state: estado atual.
        @return ações possíveis"""
        
        actions = [1,-1,1,-1,1,-1,1,-1] # Supõe que todas as ações (menos na diagonal) são possíveis

        # @TODO: Implementação do aluno

        row = state.row
        col = state.col 

        print( self.mazeBelief.maxRows )
        print( self.mazeBelief.maxColumns )
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

        return actions

    def getActionCost(self, action):
        """Retorna o custo da ação.
        @param action:
        @return custo da ação"""
        if (action == N or action == L or action == O or action == S):
            return 1.0
        else:
            return 1.5

    def goalTest(self, currentState):
        """Testa se alcançou o estado objetivo.
        @param currentState: estado atual.
        @return True se o estado atual for igual ao estado objetivo."""
        return currentState == self.goalState # Operador de igualdade definido em __eq__ no arquivo state.py
