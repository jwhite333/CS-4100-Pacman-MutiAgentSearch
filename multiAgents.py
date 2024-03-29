# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util
from math import inf
from copy import copy

from game import Agent

def GetGhostAversion(position, ghostStates):
    ghostAversion = 0
    for ghost in ghostStates:
        if ghost.scaredTimer == 0:
            ghostPosition = ghost.getPosition()
            distance = manhattanDistance(position, ghostPosition)
            if distance <= 1:
                ghostAversion = min(ghostAversion, -500 + 250 * distance)
    return ghostAversion

def GetAStarDist(position, ghostStates, destination, wallGrid):
    wallGridTemp = wallGrid.copy()  

    possibleMoves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    fringe = util.PriorityQueue()
    exploredNodes = [position]
    x,y = position

    if position == destination:
        return 0

    for dx,dy in possibleMoves:
        if not wallGridTemp[x + dx][y + dy]:
            newPosition = (x + dx, y + dy)
            if newPosition != destination:
                fringe.push([position, newPosition], 1 + manhattanDistance(newPosition, destination))
            else:
                return 1

    while not fringe.isEmpty():
        path = fringe.pop()
        node = path[-1]

        if node == destination:
            return len(path) - 1
        
        if node not in exploredNodes:
            exploredNodes.append(node)
            nodeX,nodeY = node
            for dx,dy in possibleMoves:
                if not wallGridTemp[nodeX + dx][nodeY + dy] and (nodeX + dx, nodeY + dy) not in exploredNodes:
                    newPath = path.copy()
                    newPath.append((nodeX + dx, nodeY + dy))
                    fringe.push(newPath, len(path) -1 + manhattanDistance((nodeX + dx, nodeY + dy), destination))

    return 99999999


def WavefrontHeuristic(position, ghostStates, foodGrid, wallGrid):
    wallGridTemp = wallGrid.copy()
    if foodGrid.count() == 0:
        return 0
    else:
        # totalFood = foodGrid.count()
        totalSquares =  (wallGridTemp.height * wallGridTemp.width) - wallGridTemp.count()
        accessibleFood = 0
        possibleMoves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Get ghost positions
        ghostPositions = []
        for ghost in ghostStates:
            if ghost.scaredTimer == 0:
                ghostPositions.append(ghost.getPosition())
        
        # Set ghost positions to be equivalent to a wall
        for x,y in ghostPositions:
            wallGridTemp[int(x)][int(y)] = True
        
        # Run wavefront on a copy of the walls grid to find food
        visitedNodes = [position]
        queue = [position]
        while len(queue):
            x,y = queue.pop()
            for dx,dy in possibleMoves:
                newPosition = (x + dx, y + dy)
                isWall = wallGridTemp[x + dx][y + dy]
                if not isWall and newPosition not in visitedNodes:
                    queue.append(newPosition)
                    visitedNodes.append(newPosition)
                    wallGridTemp[x + dx][y + dy] = False
                    if foodGrid[x + dx][y + dy]:
                        accessibleFood = accessibleFood + 1
        # return totalFood - accessibleFood
        return totalSquares - len(visitedNodes) - len(ghostPositions)

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        # # print("Evaluating action")
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        # print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        pacX,pacY = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        inaccessableSquares = WavefrontHeuristic((pacX, pacY), newGhostStates, newFood, successorGameState.getWalls())
        minFoodDistance = 999999
        for (foodX, foodY) in newFood.asList():
            distance = GetAStarDist((pacX, pacY), newGhostStates, (foodX,foodY), successorGameState.getWalls())
            minFoodDistance = min(minFoodDistance, distance)
                
        ghostAversion = GetGhostAversion((pacX, pacY), newGhostStates)
        foodScore = 100 * (currentGameState.getFood().count() - successorGameState.getFood().count())
        gameWinBonus = 1000 if newFood.count() == 0 else 500 if newFood.count() == 1 else 0
        if newFood.count() == 0:
            minFoodDistance = 0

        "*** YOUR CODE HERE ***"
        utility = 5 * inaccessableSquares + foodScore + ghostAversion - minFoodDistance + gameWinBonus
        
        return utility
def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

def ActionPreference(actionOne, actionTwo):
    if actionOne == "South" and actionTwo == "Stop":
        return actionTwo
    else:
        return actionTwo

def MaxValue(gameState, action, depth, depthLimit, recursionLevel, doLogging, evalFunction):

    # Log starting info
    indent = ""
    for _ in range(0, recursionLevel):
        indent = indent + "  "
    if doLogging:
        print("{0}Max(agent={1}, action={2}, depth={3}, depthLimit={4})".format(indent, "pacman", action, depth, depthLimit))

    # Check for terminal state
    if gameState.isWin() or gameState.isLose() or depth == depthLimit:
        if doLogging:
            print("{0}Terminal State, returning (action={1}, score={2})".format(indent + "  ", action, scoreEvaluationFunction(gameState)))
        return evalFunction(gameState)

    # Calculate max action recursively
    else:
        maxValue = -inf
        nextAgent = 1
        for nextAction in gameState.getLegalActions(0):
            nextState = gameState.generateSuccessor(0, nextAction)
            result = MinValue(nextState, nextAction, depth, depthLimit, nextAgent, recursionLevel + 1, doLogging, evalFunction)
            if result > maxValue:
                maxValue = result

        # Log ending info
        if doLogging:
            print("{0}Max returning cost={1} for action={2}".format(indent, maxValue, action))
        return maxValue

def MinValue(gameState, action, depth, depthLimit, agentIndex, recursionLevel, doLogging, evalFunction):

    # Log starting info
    indent = ""
    for _ in range(0, recursionLevel):
        indent = indent + "  "
    if doLogging:
        print("{0}Min(agent={1}, action={2}, depth={3}, depthLimit={4})".format(indent, agentIndex, action, depth, depthLimit))
    
    # Get next agent
    nextAgent = (agentIndex + 1) % gameState.getNumAgents()
    
    # Check for terminal state
    if gameState.isWin() or gameState.isLose() or depth == depthLimit: # or (nextAgent == 0 and depth + 1 == depthLimit):
        if doLogging:
            print("{0}Terminal State, returning (action={1}, score={2})".format(indent + "  ", action, scoreEvaluationFunction(gameState)))
        return evalFunction(gameState)

    # Calculate min action recursively
    else:
        minValue = inf
        for nextAction in gameState.getLegalActions(agentIndex):
            nextState = gameState.generateSuccessor(agentIndex, nextAction)
            if nextAgent == 0:
                result = MaxValue(nextState, nextAction, depth + 1, depthLimit, recursionLevel + 1, doLogging, evalFunction)
            else:
                result = MinValue(nextState, nextAction, depth, depthLimit, nextAgent, recursionLevel + 1, doLogging, evalFunction)
            if result < minValue:
                minValue = result

        # Log ending info
        if doLogging:
            print("{0}Min returning cost={1} for action={2}".format(indent, minValue, action))
        return minValue

def Minimax(gameState, agentIndex, depth, depthLimit, doLogging, evalFunction):
    maxValue = -inf
    bestAction = None
    for action in gameState.getLegalActions(agentIndex):
        nextState = gameState.generateSuccessor(agentIndex, action)
        result = MinValue(nextState, action, depth, depthLimit, 1, 0, doLogging, evalFunction)
        if result > maxValue:
            maxValue = result
            bestAction = copy(action)
    if doLogging:
        print(bestAction)
    return bestAction

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        return Minimax(gameState, 0, 0, self.depth, False, self.evaluationFunction)
        # util.raiseNotDefined()

def ABMaxValue(gameState, action, depth, depthLimit, recursionLevel, doLogging, evalFunction, alpha, beta):

    # Log starting info
    indent = ""
    for _ in range(0, recursionLevel):
        indent = indent + "  "
    if doLogging:
        print("{0}Max(agent={1}, action={2}, depth={3}, depthLimit={4}, alpha={5}, beta={6})".format(indent, "pacman", action, depth, depthLimit, alpha, beta))

    # Check for terminal state
    if gameState.isWin() or gameState.isLose() or depth == depthLimit:
        if doLogging:
            print("{0}Terminal State, returning (action={1}, score={2})".format(indent + "  ", action, scoreEvaluationFunction(gameState)))
        return evalFunction(gameState)

    # Calculate max action recursively
    else:
        maxValue = -inf
        nextAgent = 1
        for nextAction in gameState.getLegalActions(0):
            nextState = gameState.generateSuccessor(0, nextAction)
            maxValue = max(maxValue, ABMinValue(nextState, nextAction, depth, depthLimit, nextAgent, recursionLevel + 1, doLogging, evalFunction, alpha, beta))
            
            alpha = max(alpha, maxValue)
            if alpha > beta:
                if doLogging:
                    print("{0}Max skipping, alpha={1}, beta={2}".format(indent, alpha, beta))
                break

        # Log ending info
        if doLogging:
            print("{0}Max returning cost={1} for action={2}".format(indent, maxValue, action))
        return maxValue

def ABMinValue(gameState, action, depth, depthLimit, agentIndex, recursionLevel, doLogging, evalFunction, alpha, beta):

    # Log starting info
    indent = ""
    for _ in range(0, recursionLevel):
        indent = indent + "  "
    if doLogging:
        print("{0}Min(agent={1}, action={2}, depth={3}, depthLimit={4}, alpha={5}, beta={6})".format(indent, agentIndex, action, depth, depthLimit, alpha, beta))
    
    # Get next agent
    nextAgent = (agentIndex + 1) % gameState.getNumAgents()
    
    # Check for terminal state
    if gameState.isWin() or gameState.isLose() or depth == depthLimit: # or (nextAgent == 0 and depth + 1 == depthLimit):
        if doLogging:
            print("{0}Terminal State, returning (action={1}, score={2})".format(indent + "  ", action, scoreEvaluationFunction(gameState)))
        return evalFunction(gameState)

    # Calculate min action recursively
    else:
        minValue = inf
        for nextAction in gameState.getLegalActions(agentIndex):
            nextState = gameState.generateSuccessor(agentIndex, nextAction)
            if nextAgent == 0:
                minValue = min(minValue, ABMaxValue(nextState, nextAction, depth + 1, depthLimit, recursionLevel + 1, doLogging, evalFunction, alpha, beta))
            else:
                minValue = min(minValue, ABMinValue(nextState, nextAction, depth, depthLimit, nextAgent, recursionLevel + 1, doLogging, evalFunction, alpha, beta))
            
            beta = min(beta, minValue)
            if alpha > beta:
                if doLogging:
                    print("{0}Min skipping, alpha={1}, beta={2}".format(indent, alpha, beta))
                break

        # Log ending info
        if doLogging:
            print("{0}Min returning cost={1} for action={2}".format(indent, minValue, action))
        return minValue

def ABMinimax(gameState, agentIndex, depth, depthLimit, doLogging, evalFunction):
    alpha = -inf
    beta = inf
    bestAction = None
    for action in gameState.getLegalActions(agentIndex):
        nextState = gameState.generateSuccessor(agentIndex, action)
        result = ABMinValue(nextState, action, depth, depthLimit, 1, 0, doLogging, evalFunction, alpha, beta)
        if result > alpha:
            alpha = result
            bestAction = copy(action)

        # beta = min(beta, result)
    if doLogging:
        print(bestAction)
    return bestAction

class AlphaBetaAgent(MultiAgentSearchAgent):
    """result
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        return ABMinimax(gameState, 0, 0, self.depth, False, self.evaluationFunction)

def ExpectedMax(gameState, action, depth, depthLimit, recursionLevel, doLogging, evalFunction):

    # Log starting info
    indent = ""
    for _ in range(0, recursionLevel):
        indent = indent + "  "
    if doLogging:
        print("{0}Max(agent={1}, action={2}, depth={3}, depthLimit={4})".format(indent, "pacman", action, depth, depthLimit))

    # Check for terminal state
    if gameState.isWin() or gameState.isLose() or depth == depthLimit:
        if doLogging:
            print("{0}Terminal State, returning (action={1}, score={2})".format(indent + "  ", action, evalFunction(gameState)))
        return evalFunction(gameState)

    # Calculate max action recursively
    else:
        maxValue = -inf
        nextAgent = 1
        for nextAction in gameState.getLegalActions(0):
            nextState = gameState.generateSuccessor(0, nextAction)
            result = ExpectedMin(nextState, nextAction, depth, depthLimit, nextAgent, recursionLevel + 1, doLogging, evalFunction)
            if result > maxValue:
                maxValue = result

        # Log ending info
        if doLogging:
            print("{0}Max returning cost={1} for action={2}".format(indent, maxValue, action))
        return maxValue

def ExpectedMin(gameState, action, depth, depthLimit, agentIndex, recursionLevel, doLogging, evalFunction):

    # Log starting info
    indent = ""
    for _ in range(0, recursionLevel):
        indent = indent + "  "
    if doLogging:
        print("{0}Min(agent={1}, action={2}, depth={3}, depthLimit={4})".format(indent, agentIndex, action, depth, depthLimit))

    # Get next agent
    nextAgent = (agentIndex + 1) % gameState.getNumAgents()

    # Check for terminal state
    if gameState.isWin() or gameState.isLose() or depth == depthLimit:
        if doLogging:
            print("{0}Terminal State, returning (action={1}, score={2}".format(indent + "  ", action, evalFunction(gameState)))
        return evalFunction(gameState)

    # Calculate min action recursively
    else:
        totalScore = 0
        legalActions = gameState.getLegalActions(agentIndex)
        for nextAction in legalActions:
            nextState = gameState.generateSuccessor(agentIndex, nextAction)
            if nextAgent == 0:
                totalScore = totalScore + ExpectedMax(nextState, nextAction, depth + 1, depthLimit, recursionLevel + 1, doLogging, evalFunction)
            else:
                totalScore = totalScore + ExpectedMin(nextState, nextAction, depth, depthLimit, nextAgent, recursionLevel + 1, doLogging, evalFunction)
        score = totalScore / len(legalActions)

        # Log ending info
        if doLogging:
            print("{0}Min returning cost={1})".format(indent, score))
        return score

def Expectimax(gameState, agentIndex, depth, depthLimit, doLogging, evalFunction):
    maxValue = -inf
    bestAction = None
    for action in gameState.getLegalActions(agentIndex):
        nextState = gameState.generateSuccessor(agentIndex, action)
        result = ExpectedMin(nextState, action, depth, depthLimit, 1, 0, doLogging, evalFunction)
        if result > maxValue:
            maxValue = result
            bestAction = copy(action)
    if doLogging:
        print(bestAction)
    return bestAction

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        return Expectimax(gameState, 0, 0, self.depth, False, self.evaluationFunction)

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    pacX,pacY = currentGameState.getPacmanPosition()
    food = currentGameState.getFood()
    ghostStates = currentGameState.getGhostStates()

    minFoodDistance = 999999
    for (foodX, foodY) in food.asList():
        distance = GetAStarDist((pacX, pacY), ghostStates, (foodX,foodY), currentGameState.getWalls())
        minFoodDistance = min(minFoodDistance, distance)
            
    ghostAversion = GetGhostAversion((pacX, pacY), ghostStates)
    totalFood = food.height * food.width
    foodScore = 100 * (totalFood - food.count())
    gameWinBonus = 1000 if food.count() == 0 else 500 if food.count() == 1 else 0
    if food.count() == 0:
        minFoodDistance = 0

    # Hunt down the ghosts
    hunterScore = 0
    for ghost in ghostStates:
        if ghost.scaredTimer != 0:
            hunterScore = 1000000 - 2000 * util.manhattanDistance((pacX, pacY), ghost.getPosition())
        else:
            hunterScore = 0

    "*** YOUR CODE HERE ***"
    utility = foodScore + ghostAversion - minFoodDistance + gameWinBonus + currentGameState.getScore() + hunterScore
    return utility

# Abbreviation
better = betterEvaluationFunction
