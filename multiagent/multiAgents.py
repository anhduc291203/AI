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

from game import Agent

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
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
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

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        """Calculating distance to the farthest food pellet"""
        newFoodList = newFood.asList()
        if newFoodList:
            min_food_distance = min(util.manhattanDistance(newPos, food) for food in newFoodList)
        else:
            min_food_distance = 1  # All food eaten

        """Calculating the distances from pacman to the ghosts. Also, checking for the proximity of the ghosts (at distance of 1) around pacman."""
        ghost_distances = [util.manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates]

        """Combination of the above calculated metrics."""
        scared_bonus = 0.0
        for i, ghost_distance in enumerate(ghost_distances):
            if newScaredTimes[i] > 0:  # Ghost is scared
                scared_bonus += max(0, 1 / ghost_distance)  # Encourage chasing nearby scared ghosts

        # Combine metrics
        return (
            successorGameState.getScore()
            + (1.0 / (min_food_distance + 1))  # Add 1 to avoid zero division
            + scared_bonus
            - 1.0 / (sum(ghost_distances) + 1)  # Penalize closeness to active ghosts
        )

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
        """
        "*** YOUR CODE HERE ***"
        def minimax(agent, depth, gameState):
            if gameState.isLose() or gameState.isWin() or depth == self.depth:  # return the utility in case the defined depth is reached or the game is won/lost.
                return self.evaluationFunction(gameState)
            
            legalActions = gameState.getLegalActions(agent)
            if not legalActions:
                return self.evaluationFunction(gameState)
            
            nextAgent = (agent + 1) % gameState.getNumAgents()
            depth = depth + 1 if nextAgent == 0 else depth
            
            if agent == 0:  # maximize for pacman
                return max(minimax(nextAgent, depth, gameState.generateSuccessor(agent, action)) for action in legalActions)
            else:  # minimize for ghosts
                return min(minimax(nextAgent, depth, gameState.generateSuccessor(agent, action)) for action in legalActions)

        """Performing maximize action for the root node i.e. pacman"""
        maximum = float("-inf")
        action = Directions.STOP
        for agentState in gameState.getLegalActions(0):
            utility = minimax(1, 0, gameState.generateSuccessor(0, agentState))
            if utility > maximum or maximum == float("-inf"):
                maximum = utility
                action = agentState

        return action

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def maximizer(agent, depth, game_state, a, b):  # maximizer function
            v = float("-inf")
            for newState in game_state.getLegalActions(agent):
                v = max(v, alphabetaprune(1, depth, game_state.generateSuccessor(agent, newState), a, b))
                if v > b:
                    return v
                a = max(a, v)
            return v

        def minimizer(agent, depth, game_state, a, b):  # minimizer function
            v = float("inf")

            next_agent = agent + 1  # calculate the next agent and increase depth accordingly.
            if game_state.getNumAgents() == next_agent:
                next_agent = 0
            if next_agent == 0:
                depth += 1

            for newState in game_state.getLegalActions(agent):
                v = min(v, alphabetaprune(next_agent, depth, game_state.generateSuccessor(agent, newState), a, b))
                if v < a:
                    return v
                b = min(b, v)
            return v

        def alphabetaprune(agent, depth, game_state, a, b):
            if game_state.isLose() or game_state.isWin() or depth == self.depth:  # return the utility in case the defined depth is reached or the game is won/lost.
                return self.evaluationFunction(game_state)

            if agent == 0:  # maximize for pacman
                return maximizer(agent, depth, game_state, a, b)
            else:  # minimize for ghosts
                return minimizer(agent, depth, game_state, a, b)

        """Performing maximizer function to the root node i.e. pacman using alpha-beta pruning."""
        utility = float("-inf")
        action = Directions.WEST
        alpha = float("-inf")
        beta = float("inf")
        for agentState in gameState.getLegalActions(0):
            ghostValue = alphabetaprune(1, 0, gameState.generateSuccessor(0, agentState), alpha, beta)
            if ghostValue > utility:
                utility = ghostValue
                action = agentState
            if utility > beta:
                return utility
            alpha = max(alpha, utility)

        return action

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
        def expectimax(agent, depth, gameState):
            # Base case: terminal state or max depth reached
            if gameState.isLose() or gameState.isWin() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            legalActions = gameState.getLegalActions(agent)
            if len(legalActions) == 0:
                return self.evaluationFunction(gameState)
            
            # Maximizing for Pacman (agent 0)
            if agent == 0:
                return max(expectimax(1, depth, gameState.generateSuccessor(agent, action)) for action in legalActions)
            
            # Minimizing for ghosts (agent > 0)
            else:
                nextAgent = agent + 1  # Move to next agent
                if nextAgent == gameState.getNumAgents():  # If we're at the last agent (last ghost), cycle back to Pacman (0)
                    nextAgent = 0
                if nextAgent == 0:  # If we're back at Pacman, increase depth
                    depth += 1
                # Calculate the expected value (average over all possible ghost actions)
                return sum(expectimax(nextAgent, depth, gameState.generateSuccessor(agent, action)) for action in legalActions) / float(len(legalActions))

        # Perform maximizing task for the root node (Pacman)
        maximum = float("-inf")
        action = Directions.WEST  # Default action if no better option is found
        for agentState in gameState.getLegalActions(0):  # Iterate over Pacman's legal actions
            utility = expectimax(1, 0, gameState.generateSuccessor(0, agentState))  # Start with the next agent (ghost)
            if utility > maximum or maximum == float("-inf"):  # Select the action with the maximum utility
                maximum = utility
                action = agentState

        return action

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    """Calculating distance to the closest food pellet"""
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newFoodList = newFood.asList()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    if newFoodList:
        min_food_distance = min(util.manhattanDistance(newPos, food) for food in newFoodList)
    else:
        min_food_distance = 1  # All food eaten

    """Calculating the distances from pacman to the ghosts. Also, checking for the proximity of the ghosts (at distance of 1) around pacman."""
    ghost_distances = [util.manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates]

    scared_bonus = 0.0
    for i, ghost_distance in enumerate(ghost_distances):
        if newScaredTimes[i] > 0:  # Ghost is scared
            scared_bonus += max(0, 1 / ghost_distance)  # Encourage chasing nearby scared ghosts
    
    """Obtaining the number of capsules available"""
    newCapsule = currentGameState.getCapsules()
    numberOfCapsules = len(newCapsule)

    """Combination of the above calculated metrics."""
    return currentGameState.getScore() + (1 / float(min_food_distance)) - (1 / (sum(ghost_distances) + 1)) - numberOfCapsules + scared_bonus

# Abbreviation
better = betterEvaluationFunction