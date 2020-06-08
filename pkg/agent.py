from model import Model
from problem import Problem
from state import State
from cardinal import action
from tree import TreeNode

VERIFICA_ACAO_BLOQUEIO = True
VERIFICA_LIMITE = True

LIMITE_BUSCA = 52 # limite de profundidade de busca no caminho

UNIFORME_COST = 0

# heuristicas implementadas
HEURISTICA_DISTS = 3
HEURISTICA_DISTS_PEN_OBSTACULOS = 4
H_OPT = 6
H_EUCL = 7
H_OPT_PEN = 8

# Funções utilitárias
def printExplored(explored):
    """Imprime os nós explorados pela busca.
    @param explored: lista com os nós explorados."""
    print("--- Explorados --- (TAM: {})".format(len(explored)))
    for state in explored:
        print(state,end=' ')
    print("\n")

def printFrontier(frontier):
    """Imprime a fronteira gerada pela busca.
    @param frontier: lista com os nós da fronteira."""
    print("--- Fronteira --- (TAM: {})".format(len(frontier)))
    for node in frontier:
        print(node,end=' ')
    print("\n")

def buildPlan(solutionNode):
    depth = solutionNode.depth
    solution = [0 for i in range(depth)]
    parent = solutionNode

    for i in range(len(solution) - 1, -1, -1):
        solution[i] = parent.action
        parent = parent.parent
    return solution


class Agent:
    """"""
    counter = -1 # Contador de passos no plano, usado na deliberação

    def __init__(self, model):
        """Construtor do agente.
        @param model: Referência do ambiente onde o agente atuará."""
        self.model = model

        self.prob = Problem()
        self.prob.createMaze(6, 6)
        
        self.prob.mazeBelief.putVerticalWall(2,4,3)
        self.prob.mazeBelief.putHorizontalWall(0,1,2)
        
        # Posiciona fisicamente o agente no estado inicial
        initial = self.positionSensor()
        self.prob.defInitialState(initial.row, initial.col,initial.boxes)
        
        # Define o estado atual do agente = estado inicial
        self.currentState = self.prob.initialState

        # Define o estado objetivo
        self.prob.defGoalState(0, 0,[(5,1),(5,4),(5,5)])
        self.model.addGoalPos(5,5)
        self.model.addGoalPos(5,4)
        #self.model.addGoalPos(5,3)
        #self.model.addGoalPos(5,2)
        self.model.addGoalPos(5,1)
        #self.model.addGoalPos(5,0)

        # Plano de busca
        self.plan = None

    def deliberate(self):
        # Primeira chamada, realiza busca para elaborar um plano
        if self.counter == -1: 
            self.plan = self.cheapestFirstSearch(H_OPT) # 0 = custo uniforme, 1 = A* com colunas, 2 = A* com dist Euclidiana
            if self.plan != None:
                self.printPlan()
            else:
                print("SOLUÇÃO NÃO ENCONTRADA")
                return -1

        # Nas demais chamadas, executa o plano já calculado
        self.counter += 1

        # Atingiu o estado objetivo 
        if self.prob.goalTest(self.currentState):
            print("!!! ATINGIU O ESTADO OBJETIVO !!!")
            return -1
        # Algo deu errado, chegou ao final do plano sem atingir o objetivo
        if self.counter >= len(self.plan):
            print("### ERRO: plano chegou ao fim, mas objetivo não foi atingido.")
            return -1
        currentAction = self.plan[self.counter]

        print("--- Mente do Agente ---")
        print("{0:<20}{1}".format("Estado atual :",self.currentState))
        print("{0:<20}{1} de {2}. Ação= {3}\n".format("Passo do plano :",self.counter + 1,len(self.plan),action[currentAction]))
        self.executeGo(currentAction)

        # Atualiza o estado atual baseando-se apenas nas suas crenças e na função sucessora
        # Não faz leitura do sensor de posição
        self.currentState = self.prob.suc(self.currentState, currentAction)
        return 1

    def executeGo(self, direction):
        """Atuador: solicita ao agente física para executar a ação.
        @param direction: Direção da ação do agente
        @return 1 caso movimentação tenha sido executada corretamente."""
        self.model.go(direction)
        return 1

    def positionSensor(self):
        """Simula um sensor que realiza a leitura do posição atual no ambiente e traduz para uma instância da classe Estado.
        @return estado que representa a posição atual do agente no labirinto."""
        pos = self.model.agentPos
        return State(pos[0],pos[1],self.model.boxPos,0)

    def hn(self, state):
        goalBoxes = self.prob.goalState.boxes
        h = 0
        distsToAgent = []
        for i in range(len(goalBoxes)):
            box = goalBoxes[i]
            sBox = state.boxes[i]
            distsToAgent.append( ( abs(sBox[0] - state.row) , abs(sBox[1] - state.col) ) )
            h += abs( box[0] - sBox[0] ) + abs( box[1] - sBox[1] )

        minDist = min(distsToAgent)
        h += minDist[0] + minDist[1] # menor distancia entre o agente e as caixas
        return h

    def hnmeans(self, state):
        goalBoxes = self.prob.goalState.boxes
        h = 0
        for gbox in goalBoxes:
            m = 0
            for sbox in state.boxes:
                m += abs( gbox[0] - sbox[0] ) + abs( gbox[1] - sbox[1] )
            h += ( m / len(state.boxes) ) + ( abs(sbox[0] - state.row) + abs(sbox[1] - state.col) )
        return h
    
    def hnwall(self, state):
        goalBoxes = self.prob.goalState.boxes
        h = 0
        distsToAgent = []
        for i in range(len(goalBoxes)):
            box = goalBoxes[i]
            sBox = state.boxes[i]
            distsToAgent.append( abs(sBox[0] - state.row) + abs(sBox[1] - state.col) + self.prob.checkWall(sBox, (state.row, state.col)) )  
            h += abs( box[0] - sBox[0] ) + abs( box[1] - sBox[1] ) + self.prob.checkWall(sBox, box)  

        minDist = min(distsToAgent)
        h += minDist # menor distancia entre o agente e as caixas
        return h
    
    def hnOptm(self, state):
        distsg = [(state.row, state.col)]
        distsg += [ box for box in self.prob.goalState.boxes ]
        dists = [ box for box in state.boxes ]
        distsg.sort()
        dists.sort()
        h = 0
        for i in range(len(dists)):
            h += abs( dists[i][0] - distsg[i][0] ) + abs( dists[i][1] - distsg[i][1] )
            h += abs( dists[i][0] - distsg[i+1][0] ) + abs( dists[i][1] - distsg[i+1][1] )
        return h
    
    def hnOptmWall(self, state):
        distsg = [(state.row, state.col)]
        distsg += [ box for box in self.prob.goalState.boxes ]
        dists = [ box for box in state.boxes ]
        distsg.sort()
        dists.sort()
        h = 0
        for i in range(len(dists)):
            h += abs( dists[i][0] - distsg[i][0] ) + abs( dists[i][1] - distsg[i][1] ) 
            h += abs( dists[i][0] - distsg[i+1][0] ) + abs( dists[i][1] - distsg[i+1][1] )
            h += self.prob.checkWall(dists[i], distsg[i]) + self.prob.checkWall(dists[i], distsg[i+1])
        return h
    

    def hnOptmEucl(self, state):
        distsg = [(state.row, state.col)]
        distsg += [ box for box in self.prob.goalState.boxes ]
        dists = [ box for box in state.boxes ]
        distsg.sort()
        dists.sort()
        h = 0
        for i in range(len(dists)):
            h += abs( dists[i][0] - distsg[i][0] ) ** 2
            h += abs( dists[i][1] - distsg[i][1] ) ** 2
            h += abs( dists[i][0] - distsg[i+1][0] ) ** 2
            h += abs( dists[i][1] - distsg[i+1][1] ) ** 2
        return h ** 0.5


    def cheapestFirstSearch(self, searchType):
        """Realiza busca com a estratégia de custo uniforme ou A* conforme escolha realizada na chamada.
        @param searchType: 0=custo uniforme, 1=A* com heurística hn1; 2=A* com hn2
        @return plano encontrado"""
        # Atributos para análise de desempenho
        treeNodesCt = 0 # contador de nós gerados incluídos na árvore
        # nós inseridos na árvore, mas que não necessitariam porque o estado 
        # já foi explorado ou por já estar na fronteira
        exploredDicardedNodesCt = 0
        frontierDiscardedNodesCt = 0 

        # Algoritmo de busca
        solution = None
        root = TreeNode(parent=None)
        root.state = self.prob.initialState
        root.gn = 0
        root.hn = 0
        root.action = -1 
        treeNodesCt += 1

        # cria FRONTEIRA com estado inicial
        frontier = []
        frontier.append(root)

        # cria EXPLORADOS - inicialmente vazia
        explored = {}

        print("\n*****\n***** INICIALIZAÇÃO ÁRVORE DE BUSCA\n*****\n")
        print("\n{0:<30}{1}".format("Nós na árvore: ",treeNodesCt))
        print("{0:<30}{1}".format("Descartados já na fronteira: ",frontierDiscardedNodesCt))
        print("{0:<30}{1}".format("Descartados já explorados: ",exploredDicardedNodesCt))
        print("{0:<30}{1}".format("Total de nós gerados: ",treeNodesCt + frontierDiscardedNodesCt + exploredDicardedNodesCt))

        while len(frontier): # Fronteira não vazia
            print("\n*****\n***** Início iteração\n*****\n")
            #printFrontier(frontier)

            selNode = frontier.pop(0) # retira nó da fronteira
            selState = selNode.state
            print("Selecionado para expansão: {}\n".format(selNode))

            # Teste de objetivo
            if selState == self.prob.goalState:
                solution = selNode
                break
            explored[ str(selState.row) + str(selState.col) + str(selState.boxes) ] = selState 
            #printExplored(explored)
            
            # Obtem ações possíveis para o estado selecionado para expansão
            actions = self.prob.possibleActions(selState) # actions é do tipo [-1, -1, -1, 1 ]
            if selNode.gn >= LIMITE_BUSCA and VERIFICA_LIMITE:
                continue

            for actionIndex, act in enumerate(actions):
                if(act < 0): # Ação não é possível
                    continue

                # INSERE NÓ FILHO NA ÁRVORE DE BUSCA - SEMPRE INSERE, DEPOIS
                # VERIFICA SE O INCLUI NA FRONTEIRA OU NÃO
                # Obtem o estado sucessor pela execução da ação <act>
                sucState = self.prob.suc(selState, actionIndex)
                
                # verifica se a acao sucessora bloqueia o tabuleiro
                if( VERIFICA_ACAO_BLOQUEIO and self.prob.isBlockAction(sucState)):
                    continue
                
                # Instancia o filho ligando-o ao nó selecionado (nSel)  
                child = selNode.addChild()
                child.state = sucState

                # Custo g(n): custo acumulado da raiz até o nó filho
                gnChild = selNode.gn + self.prob.getActionCost(actionIndex)
                
                if searchType == UNIFORME_COST:
                    child.setGnHn(gnChild, 0) # Deixa h(n) zerada porque é busca de custo uniforme

                elif searchType == HEURISTICA_DISTS:
                    child.setGnHn(gnChild, self.hn(sucState) )

                elif searchType == HEURISTICA_DISTS_PEN_OBSTACULOS:
                    child.setGnHn(gnChild, self.hnwall(sucState) )

                elif searchType == H_OPT:
                    child.setGnHn(gnChild, self.hnOptm(sucState) )

                elif searchType == H_EUCL:
                    child.setGnHn(gnChild, self.hnOptmEucl(sucState) )

                elif searchType == H_OPT_PEN:
                    child.setGnHn(gnChild, self.hnOptmWall(sucState) )
                child.action = actionIndex
                # INSERE NÓ FILHO NA FRONTEIRA (SE SATISFAZ CONDIÇÕES)
                alreadyExplored = False

                # Testa se estado do nó filho foi explorado
                expHash = str(child.state.row) + str(child.state.col) + str(child.state.boxes)
                if expHash in explored:
                    exp = explored[expHash]
                    if( child.state.cost >= exp.cost ):
                        alreadyExplored = True

                # Testa se estado do nó filho está na fronteira, caso esteja
                # guarda o nó existente em nFront
                nodeFront = None
                if not alreadyExplored:
                    for node in frontier:
                        if(child.state == node.state and child.state.row == node.state.row and child.state.col == node.state.col ):
                            nodeFront = node
                            break
                # Se ainda não foi explorado
                if not alreadyExplored:
                    # e não está na fronteira, adiciona à fronteira
                    if nodeFront == None:
                        # adiciona na fronteira se a acao nao bloqueia a solucao
                        frontier.append(child)
                        frontier.sort(key=lambda x: ( x.getFn() , x.hn ) ) # Ordena a fronteira pelo f(n), usando o valor de hn como desempate
                        treeNodesCt += 1
                        
                    else:
                        # Se já está na fronteira temos que ver se é melhor
                        if nodeFront.getFn() > child.getFn():       # Nó da fronteira tem custo maior que o filho
                            frontier.remove(nodeFront)              # Remove nó da fronteira (pior e deve ser substituído)
                            nodeFront.remove()                      # Retira-se da árvore 
                            frontier.append(child)                  # Adiciona filho que é melhor
                            #frontier.sort(key=lambda x: x.getFn() )  # Ordena a fronteira pelo f(n), ascendente
                            frontier.sort(key=lambda x: ( x.getFn() , x.hn ) )  # Ordena a fronteira pelo f(n), usando o valor de hn como desempate
                            # treeNodesCt não é incrementado por inclui o melhor e retira o pior
                        else:
                            # Conta como descartado porque o filho é pior que o nó da fronteira e foi descartado
                            frontierDiscardedNodesCt += 1
                else:
                    exploredDicardedNodesCt += 1
            
            print("\n{0:<30}{1}".format("Nós na árvore: ",treeNodesCt))
            print("{0:<30}{1}".format("Descartados já na fronteira: ",frontierDiscardedNodesCt))
            print("{0:<30}{1}".format("Descartados já explorados: ",exploredDicardedNodesCt))
            print("{0:<30}{1}".format("Total de nós gerados: ",treeNodesCt + frontierDiscardedNodesCt + exploredDicardedNodesCt))


        if(solution != None):
            print("!!! Solução encontrada !!!")
            print("!!! Custo:        {}".format(solution.gn))
            print("!!! Profundidade: {}\n".format(solution.depth))
            print("\n{0:<30}{1}".format("Nós na árvore: ",treeNodesCt))
            print("{0:<30}{1}".format("Descartados já na fronteira: ",frontierDiscardedNodesCt))
            print("{0:<30}{1}".format("Descartados já explorados: ",exploredDicardedNodesCt))
            print("{0:<30}{1}".format("Total de nós gerados: ",treeNodesCt + frontierDiscardedNodesCt + exploredDicardedNodesCt))
            return buildPlan(solution)
        else:
            print("### Solução NÃO encontrada ###")
            return None

    def printPlan(self):
        """Apresenta o plano de busca."""    
        print("--- PLANO ---")
        # @TODO: Implementação do aluno
        for plannedAction in self.plan:
            print("{} > ".format(action[plannedAction]),end='')
        print("FIM\n\n")
