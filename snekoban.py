import json
import typing

direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    
    {"computers": {(1,2), (2,3)}, "player": (2,2), "walls": {(3,2), (3,3)}
     "targets": {4,3), (2,3))}}
    """
    board = {"walls": set(), "computers": set(), "targets": set(), "player": ()}
    
    for row in range(len(level_description)):
        for col in range(len(level_description[row])):
            if len(level_description[row][col]) == 0:   
                pass
            else:
                for item in level_description[row][col]:
                    if item == "wall":
                        board["walls"].add((row, col))
                    elif item == "computer":
                        board["computers"].add((row, col))
                    elif item == "target":
                        board["targets"].add((row, col)) 
                    elif item == "player":
                        board["player"] = (row, col)
    board["rows"] = len(level_description)
    board["cols"] = len(level_description[0])

    return board


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    for target_pos in game["targets"]:
        if target_pos not in game["computers"]:
            return False
    if len(game["targets"]) == 0:
        return False
    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    row = game["player"][0]
    col = game["player"][1]
    if direction == "up":
        new_pos = (row-1, col)
        next_pos = (row-2, col)
    if direction == "down":
        new_pos = (row+1, col)
        next_pos = (row+2, col)
    if direction == "right":
        new_pos = (row, col+1)
        next_pos = (row, col+2)
    if direction == "left":
        new_pos = (row, col-1)
        next_pos = (row, col-2)
      
    #create new game object
    copy_game = {"walls": set(), "computers": set(), "targets": set(), "player": (),
                "rows": game["rows"], "cols": game["cols"]}
    for pos in game["walls"]:
        copy_game["walls"].add((pos[0], pos[1]))
    for pos in game["computers"]:
        copy_game["computers"].add((pos[0], pos[1]))
    for pos in game["targets"]:
        copy_game["targets"].add((pos[0], pos[1]))
    player_pos = game["player"]
    copy_game["player"] = (player_pos[0], player_pos[1])

    if new_pos in game["computers"]:
        push_computer(copy_game, new_pos, next_pos)
    elif new_pos not in game["walls"]:
        copy_game["player"] = new_pos

    return copy_game
    
def push_computer(game, new_pos, next_pos):
    """
    Pushes computer in game if allowed, given game state, the new position of
    the player to be moved to, and the next position after new_pos in the 
    direction the player is going.
    """
    if next_pos not in game["computers"] and next_pos not in game["walls"]:
        game["computers"].remove(new_pos)
        game["computers"].add(next_pos)
        game["player"] = new_pos


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    Ex: given
    {'walls': {(4, 0), (5, 4), (4, 6), (5, 1), (0, 2), (0, 5), (1, 0), (1, 6), 
               (3, 0), (5, 0), (5, 6), (3, 6), (5, 3), (0, 1), (1, 2), (0, 4), 
               (5, 2), (5, 5), (0, 0), (0, 3), (2, 0), (0, 6), (2, 6)}, '
     computers': {(2, 3), (2, 4), (3, 2)}, 
     'targets': {(1, 1), (4, 1), (2, 1)}, 
     'player': (2, 2)
     'rows': 6, 
     'cols': 7}
    returns
    [
     [['wall'], ['wall'], ['wall'], ['wall'], ['wall'], ['wall']], 
     [['wall'], [], ['computer'], [], [], ['wall']], 
     [['wall'], [], [], ['target', 'player'], [], ['wall']], 
     [['wall'], ['wall'], ['wall'], ['wall'], ['wall'], ['wall']]]
    """
    old_game = []
    
    for row in range(game["rows"]):
        old_game.append([])
        for col in range(game["cols"]):
            old_game[row].append([])
    for pos in game["walls"]:
        old_game[pos[0]][pos[1]].append("wall")
    for pos in game["computers"]:
        old_game[pos[0]][pos[1]].append("computer")
    for pos in game["targets"]:
        old_game[pos[0]][pos[1]].append("target")
    player_pos = game["player"]
    old_game[player_pos[0]][player_pos[1]].append("player")

    return old_game

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    agenda = [()] 
    #list of tuples of computer pos, and position tuples (paths)
    #ex: [ ( "up", "down", "left") ,
        #  ( "left", "right" ) ]
    
    visited = { (tuple(game["computers"]), game["player"]), } 
    #set of tuples of computer pos and visted positions
    #ex: { ( { (1,1), (1,2) },  computer positions
    #          (3,2) ), } player postion
    
    game_states = [game]
    #list of dictionary game states associated with each path in agenda
    
    if victory_check(game):
        return []

    while len(agenda) != 0:
        path = agenda.pop(0) #first player path
        cur_game = game_states.pop(0)
        
        next_game = step_game(cur_game, "up")
        if check_child(next_game, agenda, visited, path, game_states, "up"):
            return list(path) + ["up"]
        
        next_game = step_game(cur_game, "down")
        if check_child(next_game, agenda, visited, path, game_states, "down"):
            return list(path) + ["down"]
        
        next_game = step_game(cur_game, "right")
        if check_child(next_game, agenda, visited, path, game_states, "right"):
            return list(path) + ["right"]
        
        next_game = step_game(cur_game, "left")
        if check_child(next_game, agenda, visited, path, game_states, "left"):
            return list(path) + ["left"]
      
    return None
    
def check_child(game, agenda, visited, path, game_states, direction):
    """
    Checks if a child game version of a game path leads to victory and returns
    True if so. Otherwise, it adds the current position of computers and the
    player to visited, and appends the path to the end of agenda, and 
    appends the game state to the end of game_states.
    """
    if ((tuple(game["computers"]), game["player"])) not in visited:
        if victory_check(game):
            #TODO
            return True #convert_to_str(path) 
        else:
            visited.add((tuple(game["computers"]), game["player"]))
            agenda.append(path + (direction,))   
            game_states.append(game)
    return False

if __name__ == "__main__":
    #example usage
    g = [
   [["wall"], ["wall"], ["wall"], ["wall"],     ["wall"],   ["wall"]],
   [["wall"], [],       [],       ["target"],   ["wall"],   ["wall"]],
   [["wall"], [],       [],       ["wall"],     ["player"], ["wall"]],
   [["wall"], [],       [],       ["computer"], [],         ["wall"]],
   [["wall"], [],       [],       [],           ["wall"],   ["wall"]],
   [["wall"], ["wall"], ["wall"], ["wall"],     ["wall"],   ["wall"]]
]
    new = new_game(g)
    print(new)
   
    new2 = step_game(new, "up")
    print(new2)
    new3 = step_game(new2, "left")
    print(new3)
    solution = solve_puzzle(new)
    print(solution)
    # old_board_back = dump_game(new)
    # print(old_board_back)

    
