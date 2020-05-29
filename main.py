import sys
sys.path.append('pkg')
from model import Model
from agent import Agent

def buildMaze(model):
    model.maze.putVerticalWall(0,1,0)
    model.maze.putVerticalWall(0,0,1)
    model.maze.putVerticalWall(5,8,1)
    model.maze.putVerticalWall(5,5,2)
    model.maze.putVerticalWall(8,8,2)

    model.maze.putHorizontalWall(4,7,0)
    model.maze.putHorizontalWall(7,7,1)
    model.maze.putHorizontalWall(3,5,2)
    model.maze.putHorizontalWall(3,5,3)
    model.maze.putHorizontalWall(7,7,3)

    model.maze.putVerticalWall(6,7,4)
    model.maze.putVerticalWall(5,6,5)
    model.maze.putVerticalWall(5,7,7)

def main():
    # Cria o ambiente (modelo) = Labirinto com suas paredes
    mazeRows = 9
    mazeColumns = 9
    model = Model(mazeRows, mazeColumns)
    buildMaze(model)

    # Define a posição inicial do agente no ambiente - corresponde ao estado inicial
    model.setAgentPos(8,0)

    # Cria um agente
    agent = Agent(model)

    model.draw()
    print("\n Início do ciclo de raciocínio do agente \n")
    while agent.deliberate() != -1:
        model.draw()


if __name__ == '__main__':
    main()
