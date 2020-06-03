import random

from model import Model
from problem import Problem
from state import State
from cardinal import action
from tree import TreeNode

VERIFICA_ACAO_BLOQUEIO = True
VERIFICA_LIMITE = True

LIMITE_BUSCA = 52 # limite de profundidade de busca no caminho

UNIFORME_COST = 0

BOX_COST = 18

# heuristicas implementadas
HEURISTICA_DISTS = 3
HEURISTICA_DISTS_PEN_OBSTACULOS = 4
H_OPT = 6
H_EUCL = 7
H_OPT_PEN = 8

POPULATION=5000
GENERATIONS=200
PROB_MUT=0.1
PROB_CROSS=0.9

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
        #self.prob.defGoalState(0, 0,[(5,1),(5,4),(5,5)])
        self.prob.defGoalState(0, 0,[(5,5),(5,2)])
        self.model.addGoalPos(5,5)
        #self.model.addGoalPos(5,4)
        #self.model.addGoalPos(5,3)
        self.model.addGoalPos(5,2)
        #self.model.addGoalPos(5,1)
        #self.model.addGoalPos(5,0)

        # Plano de busca
        self.plan = None

    def deliberate(self):
        # Primeira chamada, realiza busca para elaborar um plano
        if self.counter == -1: 
            self.plan = self.geneticSearch() # 0 = custo uniforme, 1 = A* com colunas, 2 = A* com dist Euclidiana
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
    
    def hnOptmNoAgent(self, state):
        
        distsg = [ box for box in self.prob.goalState.boxes ]
        dists = [ box for box in state.boxes ]
        distsg.sort()
        dists.sort()
        h = 0
        for i in range(len(dists)):
            h += abs( dists[i][0] - distsg[i][0] ) + abs( dists[i][1] - distsg[i][1] )
            pos = 0 if i == len(dists) else i
            h += abs( dists[i][0] - distsg[pos][0] ) + abs( dists[i][1] - distsg[pos][1] )
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

    def geneticSearch(self):
        actionsCount = 40
        population = self.generate(actionsCount, POPULATION)
        mutate_only_childs = True
        for gen in range(GENERATIONS):
             
            initialState = State(self.prob.initialState.row, self.prob.initialState.col, [ box for box in self.prob.initialState.boxes], self.prob.initialState.cost)
            for pop in population:
                self.fitness(pop, actionsCount, initialState)
            
            childs = []
            pairs = self.roulette(population,actionsCount)
            for i in range( len(pairs) - 2 ):
                if random.random() < PROB_CROSS:
                    
                    for child in self.crossover(pairs[i],pairs[i+1]):
                        childs.append(child)
            
            if mutate_only_childs:
                for plan in childs:
                    self.mutation(plan, actionsCount)
                    population.append(plan)
            else:
                for child in childs:
                    population.append(childs)
                for plan in population:
                    self.mutation(plan, actionsCount)
                

            initialState = State(self.prob.initialState.row, self.prob.initialState.col, [ box for box in self.prob.initialState.boxes], self.prob.initialState.cost)
            population = self.survival(population, initialState, actionsCount)
            
            if(population[0][actionsCount] == 0):
                print("break")
                print(population[0][actionsCount])
                print(population[0])

                break

            print(population[0])
            print(gen)

        return population[0][:actionsCount]


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
        explored = []

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
            explored.append(selState)
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
                for node in explored:
                    if(child.state == node and child.state.row == node.row and child.state.col == node.col and child.state.cost >= node.cost ):
                        alreadyExplored = True
                        break

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
                        frontier.sort(key=lambda x: x.getFn()) # Ordena a fronteira pelo f(n), ascendente
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

    def generate(self, actionsCount, populationSize):
        population = [ [ random.randint(0,3) for a in range(actionsCount) ] for pop in range(populationSize) ]
        for pop in population:
            pop.append(actionsCount)
        return population
        
    def roulette(self, population, actionsCount):
        pairs = []
        roulete = [ plan for plan in population ]
        for _ in range(len(population)):
            winner = self.draw(roulete, actionsCount)
            pairs.append(roulete.pop(winner))
        return pairs

    def draw(self, roulette, actionsCount):
        fitnesssum = sum([ actionsCount - r[len(r)-1] for r in roulette ])
        roulettewheel = []
        for r in roulette:
            roulettewheel.append( actionsCount - r[len(r)-1] / fitnesssum )        
        drawpoint = random.random()
        sumRoulette = 0
        i = -1
        while sumRoulette < drawpoint:
            i += 1 
            sumRoulette += roulettewheel[i]
        return i if i > 0 else 0       

    def crossover(self,father, mother):
        childs = [[],[]]                    
        crosspoint = random.randint(0,len(father))
        for i in range(len(father)):
            if i <= crosspoint:
                childs[0].append(father[i])
                childs[1].append(mother[i])
            else:
                childs[1].append(father[i])
                childs[0].append(mother[i])
        return childs

    def mutation(self, plan, actionsCount):        
        for i in range(actionsCount):
            if random.random() < PROB_MUT :
                a = plan[i]
                a += 1
                a = 0 if a > 3 else a
                plan[i] = a

    def fitness(self, plan, actionsCount, initialState):
        state = State(initialState.row, initialState.col, [ box for box in initialState.boxes], initialState.cost)
        heuristic = 0
        
        for i in range(actionsCount):
            action = plan[i]
            state = self.prob.suc(state, action)
            if self.prob.isBlockAction(state):
                heuristic = 1000
                break

        if state == self.prob.goalState:
            print(plan)
            print("plan goalstate")
            plan[actionsCount] = 0
        else:
            heuristic = self.hnOptmEucl(state) + ( 1000 if self.prob.isBlockAction(state) else 0 )
            plan[actionsCount] = heuristic


    def survival(self, population, initialState, actionsCount):
        for plan in population:
            self.fitness(plan, actionsCount, initialState)
        
        population.sort(key=lambda x : int(x[actionsCount]))
        
        return population[:POPULATION]

