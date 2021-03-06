import sys
sys.path.append('pkg')
from model import Model
from agent import Agent

def buildMaze(model):
    model.maze.putVerticalWall(2,4,3)
    model.maze.putHorizontalWall(0,1,2)
    
def main():
    # Cria o ambiente (modelo) = Labirinto com suas paredes
    mazeRows = 6
    mazeColumns = 6
    model = Model(mazeRows, mazeColumns)
    buildMaze(model)

    # Define a posicao inicial do agente no ambiente - corresponde ao estado inicial
    model.setAgentPos(3,0)
    model.addBoxPos(1,1)
    model.addBoxPos(1,3)
    model.addBoxPos(2,2)
    #model.addBoxPos(3,4)
    #model.addBoxPos(4,1)
    
    # Cria um agente
    agent = Agent(model)

    model.draw()
    print("\n Início do ciclo de raciocinio do agente \n")
    while agent.deliberate() != -1:
        model.draw()


if __name__ == '__main__':
    main()
