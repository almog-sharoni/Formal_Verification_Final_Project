# @ - keeper
# + - keeper on goal
# $ - box
# * - box on goal
# # - wall
# . - goal
# - - floor
def parse_board(xsb_input):
    '''Parses the XSB representation.

    Returns:

    '''


    board_array = []
    keeper_x = -1
    keeper_y = -1
    for row in xsb_input.strip().splitlines():
        row_array = []
        for cell in row:
            if cell == "@":
                row_array.append("KEEPER")
                keeper_x = row.index(cell)
                keeper_y = xsb_input.strip().splitlines().index(row)
            if cell == "+":
                row_array.append("KEEPER_ON_GOAL")
                keeper_x = row.index(cell)
                keeper_y = xsb_input.strip().splitlines().index(row)
            if cell == "$":
                row_array.append("BOX")
            if cell == "*":
                row_array.append("BOX_ON_GOAL")
            if cell == "#":
                row_array.append("WALL")
            if cell == ".":
                row_array.append("GOAL")
            if cell == "-":
                row_array.append("FLOOR")
        board_array.append(row_array)



    return board_array, keeper_x, keeper_y

def generate_smv_define(board):
    smv_define = f'''
        rows := {len(board)};
        columns := {len(board[0])};

        '''

    return smv_define


def generate_smv_var(board, keeper_x, keeper_y):
    rows = len(board)
    columns = len(board[0])

    smv_var = f'''
        --Cell: {"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL", "BOX_ON_GOAL", "WALL", "FLOOR"};
        
        --board : array 0..{rows-1} of array 0..{columns-1} of Cell;
        
        -- board : array 0..{rows-1} of array 0..{columns-1} of {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL", "#", "FLOOR", "BOX_ON_GOAL"}}; 
        board : array -2..{rows+1} of array -2..{columns+1} of {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL","WALL" , "FLOOR", "BOX_ON_GOAL"}};  
        
        keeper_x : 0..{rows-1};
        keeper_y : 0..{columns-1};

        action : {{u, d, l, r, 0}};  
        
    '''


    return smv_var

def generate_smv_state(board, keeper_x, keeper_y):
    smv_state = f''' 
            init(action) := 0;
            init(keeper_x) := {keeper_x};
            init(keeper_y) := {keeper_y};
            
            '''

    for x in range(len(board)):
        for y in range(len(board[0])):
            print("index", x, y)
            smv_state += f'''
                        init(board[{x}][{y}]) := "{board[x][y]}";
                    '''

    # smv_state += initWalls(board_data["walls"])

    # Movement Constraints (Iterative)
    smv_state += f'''
    
        -- dont need to refer the borders as we have walls
        next(action) := {{u, d, l, r, 0}};
    
    
        next(keeper_x) := case
                keeper_x = {len(board)} - 1 : keeper_x; -- Cannot move right if at the right edge
                keeper_x = 0 : keeper_x; -- Cannot move left if at the left edge
                (next(action) = u) & (board[keeper_x - 1][keeper_y] = "BOX" | board[keeper_x - 1][keeper_y] = "BOX_ON_GOAL") & (board[keeper_x - 2][keeper_y] = "FLOOR" | board[keeper_x - 2][keeper_y] = "GOAL") : keeper_x - 1;  -- Can move up if there is a box above
                (next(action) = u) & (board[keeper_x - 1][keeper_y] = "FLOOR" | board[keeper_x - 1][keeper_y] = "GOAL") : keeper_x - 1;  -- Can move up if there is floor or goal above
    
                (next(action) = d) & (board[keeper_x + 1][keeper_y] = "BOX" | board[keeper_x + 1][keeper_y] = "BOX_ON_GOAL") & (board[keeper_x + 2][keeper_y] = "FLOOR" | board[keeper_x + 2][keeper_y] =  "GOAL"): keeper_x + 1;  -- Can move down if there is a box below
                (next(action) = d) & (board[keeper_x + 1][keeper_y] = "FLOOR" | board[keeper_x + 1][keeper_y] = "GOAL"): keeper_x + 1;  -- Can move down if there is floor or goal below
    
                TRUE : keeper_x;  -- Default: stay in the same position if no valid move
        esac;
    
        next(keeper_y) :=  case
                keeper_y = {len(board[0])} - 1 : keeper_y; -- Cannot move right if at the right edge
                keeper_y = 0 : keeper_y; -- Cannot move left if at the left edge
                (next(action) = l) & (board[keeper_x][keeper_y - 1] = "BOX" | board[keeper_x][keeper_y - 1] = "BOX_ON_GOAL") & (board[keeper_x][keeper_y - 2] = "FLOOR" | board[keeper_x][keeper_y - 2] = "GOAL"): keeper_y - 1;  -- Can move left if there is a box to the left
                (next(action) = l) & (board[keeper_x][keeper_y - 1] = "FLOOR" | board[keeper_x][keeper_y - 1] = "GOAL"): keeper_y - 1;  -- Can move left if there is floor or goal to the left
    
                (next(action) = r) & (board[keeper_x][keeper_y + 1] = "BOX" | board[keeper_x][keeper_y + 1] =  "BOX_ON_GOAL") & (board[keeper_x][keeper_y + 2] = "FLOOR" | board[keeper_x][keeper_y + 2] = "GOAL") : keeper_y + 1;  -- Can move right if there is a box to the right
                (next(action) = r) & (board[keeper_x][keeper_y + 1] = "FLOOR" | board[keeper_x][keeper_y + 1] =  "GOAL"): keeper_y + 1;  -- Can move right if there is floor or goal to the right
    
                TRUE : keeper_y;  -- Default: stay in the same position if no valid move
        esac;
    
        '''

    for x in range(len(board)):
        for y in range(len(board[0])):
            smv_state += f'''
                next(board[{x}][{y}]) := case
                    next(keeper_x) = {x} & next(keeper_y) = {y} : "KEEPER"; -- Keeper moves to this position
        
                    -- if keeper is on x,y and he moves to another position, and board[x][y] is "KEEPER_ON_GOAL", then it becomes "GOAL"
                    board[{x}][{y}] = "KEEPER_ON_GOAL" & next(keeper_x) !={x} | next(keeper_y) != {y} : "GOAL";
                    
                    -- if keeper is on x,y and he moves to another position, and board[x][y] is "KEEPER", then it becomes "FLOOR"
                    board[{x}][{y}] = "KEEPER" & next(keeper_x) !={x} | next(keeper_y) != {y} : "FLOOR";
                    
                    -- if keeper moves to x,y, then it becomes "KEEPER"
                    next(keeper_x) = {x} & next(keeper_y) = {y} : "KEEPER";
                    
                    -- if board[x][y] is "FLOOR" and board[x+2][y] is "KEEPER" or "KEEPER_ON_GOAL" and board[x+1][y] is "BOX" or "BOX_ON_GOAL", and next(action) is "u" then it becomes "BOX"
                    
                    board[{x}][{y}] = "FLOOR" & (board[{x+2}][{y}] = "KEEPER" | board[{x+2}][{y}] = "KEEPER_ON_GOAL") & board[{x+1}][{y}] = "BOX" & next(action) = u : "BOX";
                    
                    board[{x}][{y}] = "GOAL" & (board[{x+2}][{y}] = "KEEPER" | board[{x+2}][{y}] = "KEEPER_ON_GOAL") & board[{x+1}][{y}] = "BOX" & next(action) = u : "BOX_ON_GOAL";
                    
                    -- if board[x][y] is "FLOOR" and board[x-2][y] is "KEEPER" or "KEEPER_ON_GOAL" and board[x-1][y] is "BOX" or "BOX_ON_GOAL"| and next(action) is "d" then it becomes "BOX"
                    board[{x}][{y}] = "FLOOR" & (board[{x-2}][{y}] = "KEEPER" | board[{x-2}][{y}] = "KEEPER_ON_GOAL") & board[{x-1}][{y}] = "BOX" & next(action) = d : "BOX";
                    
                    -- if board[x][y] is "GOAL" and board[x-2][y] is "KEEPER" or "KEEPER_ON_GOAL" and board[x-1][y] is "BOX" or "BOX_ON_GOAL"| and next(action) is "d" then it becomes "BOX"
                    board[{x}][{y}] = "GOAL" & (board[{x-2}][{y}] = "KEEPER" | board[{x-2}][{y}] = "KEEPER_ON_GOAL") & board[{x-1}][{y}] = "BOX" & next(action) = d : "BOX_ON_GOAL";
                    
                    -- if board[x][y] is "FLOOR" and board[x][y+2] is "KEEPER" or "KEEPER_ON_GOAL" and board[x][y+1] is "BOX" or "BOX_ON_GOAL"| and next(action) is "l" then it becomes "BOX"
                    board[{x}][{y}] = "FLOOR" & (board[{x}][{y+2}] = "KEEPER" | board[{x}][{y+2}] = "KEEPER_ON_GOAL") & board[{x}][{y+1}] = "BOX" & next(action) = l : "BOX";
                    
                    -- if board[x][y] is "GOAL" and board[x][y+2] is "KEEPER" or "KEEPER_ON_GOAL" and board[x][y+1] is "BOX" or "BOX_ON_GOAL"| and next(action) is "l" then it becomes "BOX"
                    board[{x}][{y}] = "GOAL" & (board[{x}][{y+2}] = "KEEPER" | board[{x}][{y+2}] = "KEEPER_ON_GOAL") & board[{x}][{y+1}] = "BOX" & next(action) = l : "BOX_ON_GOAL";
                    
                    --default
                    TRUE : board[{x}][{y}];
                esac;
            '''

    # TODO: should add more box movement constraints here (e.g., preventing two-box pushes and box-wall collisions)

    return smv_state





def generate_smv_win_spec(board_data):
    '''Encodes the LTL win condition in SMV syntax.

    Returns:
        String containing the SMV specification
    '''
    smv_win_spec = f'''
    -- Win condition: all boxes are on goals

    '''
    for x in range(len(board_data)):
        for y in range(len(board_data[0])):
            if board_data[x][y] == "BOX_ON_GOAL" or board_data[x][y] == "GOAL":
                smv_win_spec += f''' board[{x}][{y}] = "BOX_ON_GOAL" '''
    return smv_win_spec


def main():
    xsb_board = '''
------
#-.--#
#-$--#
#-@#-#
------
'''  # Example board

    board_data, keeper_x, keeper_y = parse_board(xsb_board)

    smv_model = f'''
    MODULE main 
    VAR
        {generate_smv_var(board_data, keeper_x, keeper_y)}

    ASSIGN
        {generate_smv_state(board_data, keeper_x, keeper_y)} 

    SPEC
    AG !(
        {generate_smv_win_spec(board_data)}
    )
 
    '''

    with open("sokoban_model.smv", "w") as f:
        f.write(smv_model)


if __name__ == "__main__":
    main()
