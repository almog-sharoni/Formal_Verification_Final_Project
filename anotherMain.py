# @ - keeper
# + - keeper on goal
# $ - box
# * - box on goal
# # - wall
# . - goal
# - - floor

def parse_board(xsb_input):
    """Parses the XSB representation.

    Returns:
       A dictionary containing:
           - wk_pos: (x, y) tuple of warehouse keeper position
           - boxes: List of (x, y) box positions
           - goals: List of (x, y) goal positions
           - walls: List of (x, y) wall positions
    """

    board = []
    for line in xsb_input.strip().splitlines():
        row = []
        for char in line:
            row.append(char)
            if char == "@":
                keeper_x = line
                keeper_y = line.index(char)
        board.append(row)

    print("board", board)
    print("keeper_x", keeper_x)
    print("keeper_y", keeper_y)

    return board, keeper_x, keeper_y

def generate_smv_define(board):
    smv_define = f"""
        rows := {len(board)};
        columns := {len(board[0])};

        """

    return smv_define


def generate_smv_var(board, keeper_x, keeper_y):

    smv_var = f"""
        Cell: {"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL", "BOX_ON_GOAL", "WALL", "FLOOR"};
        # צריך לשנות את כל הסימבולים לשמות האלה
        board : array 0..rows-1 of array 0..columns-1 of Cell;
        
        -- board : array 0..rows-1 of array 0..columns-1 of {{'@', '$', '.', '+', '#', '-', '*'}}; 
        
        keeper_x : 0..rows-1;
        keeper_y : 0..columns-1;

        action : {{u, d, l, r, 0}};  

    """

    return smv_var

def generate_smv_state(board, keeper_x, keeper_y):
    smv_state = f""" 
            init(action) := 0;
            init(keeper_x) := {keeper_x};
            init(keeper_y) := {keeper_y};
            
            """

    for x in range(len(board)):
        for y in range(len(board[0])):
            print("index", x, y)
            smv_state += f"""
                        init(board[{x}][{y}]) := {board[x][y]};
                    """

    # smv_state += initWalls(board_data['walls'])

    # Movement Constraints (Iterative)
    smv_state += f"""
    
        -- dont need to refer the borders as we have walls
        next(action) := {{u, d, l, r, 0}};
    
    
        next(keeper_x) := case
                -- keeper_x = columns - 1 : keeper_x; -- Cannot move right if at the right edge
                (next(action) = u) & (board[keeper_x-1][keeper_y] = {'$','*'}) & (board[keeper_x-2][keeper_y] = {'-', '.'}) : keeper_x - 1;  -- Can move up if there is a box above
                (next(action) = u) & (board[keeper_x-1][keeper_y] = {'-', '.'}) : keeper_x - 1;  -- Can move up if there is floor or goal above
    
                (next(action) = d) & (board[keeper_x+1][keeper_y] = {'$','*'}) & (board[keeper_x+2][keeper_y] = {'-', '.'}): keeper_x + 1;  -- Can move down if there is a box below
                (next(action) = d) & (board[keeper_x+1][keeper_y] = {'-', '.'}): keeper_x + 1;  -- Can move down if there is floor or goal below
    
                TRUE : keeper_x;  -- Default: stay in the same position if no valid move
        esac;
    
        next(keeper_y) :=  case
                (next(action) = l) & (board[keeper_x][keeper_y-1] = {'$', '*'}) & (board[keeper_x][keeper_y-2] = {'-', '.'}): keeper_y - 1;  -- Can move left if there is a box to the left
                (next(action) = l) & (board[keeper_x][keeper_y-1] = {'-', '.'}): keeper_y - 1;  -- Can move left if there is floor or goal to the left
    
                (next(action) = r) & (board[keeper_x][keeper_y+1] = {'$', '*'}) & (board[keeper_x][keeper_y+2] = {'-', '.'}) : keeper_y + 1;  -- Can move right if there is a box to the right
                (next(action) = r) & (floors[keeper_x][keeper_y+1] = {'-', '.'}): keeper_y + 1;  -- Can move right if there is floor or goal to the right
    
                TRUE : keeper_y;  -- Default: stay in the same position if no valid move
        esac;
    
        """

    for x in range(len(board)):
        for y in range(len(board[0])):
            smv_state += f"""
                next(board[{x}][{y}]) := case
                    next(keeper_x) = {x} & next(keeper_y) = {y} : '@'; -- Keeper moves to this position
        
                    -- if keeper is on x,y and he moves to another position, and board[x][y] is '+', then it becomes '.'
                    board[{x}][{y}] = '+' & next(keeper_x) !={x} | next(keeper_y) != {y} : '.';
                    
                    -- if keeper is on x,y and he moves to another position, and board[x][y] is '@', then it becomes '-'
                    board[{x}][{y}] = '@' & next(keeper_x) !={x} | next(keeper_y) != {y} : '-';
                    
                    -- if keeper moves to x,y, then it becomes '@'
                    next(keeper_x) = {x} & next(keeper_y) = {y} : '@';
                    
                    -- if board[x][y] is '-' and board[x+2][y] is '@' or '+' and board[x+1][y] is '$' or '*', and next(action) is 'u' then it becomes '$'
                    board[{x}][{y}] = '-' & (board[{x+2}][{y}] = {'@', '+'}) & board[{x+1}][{y}] = '$' & next(action) = u : '$';
                    
                    -- if board[x][y] is '.' and board[x+2][y] is '@' or '+' and board[x+1][y] is '$' or '*', and next(action) is 'u' then it becomes '$'
                    board[{x}][{y}] = '.' & (board[{x+2}][{y}] = {'@', '+'}) & board[{x+1}][{y}] = '$' & next(action) = u : '*';
                    
                    -- if board[x][y] is '-' and board[x-2][y] is '@' or '+' and board[x-1][y] is '$' or '*', and next(action) is 'd' then it becomes '$'
                    board[{x}][{y}] = '-' & (board[{x-2}][{y}] = {'@', '+'}) & board[{x-1}][{y}] = '$' & next(action) = d : '$';
                    
                    -- if board[x][y] is '.' and board[x-2][y] is '@' or '+' and board[x-1][y] is '$' or '*', and next(action) is 'd' then it becomes '$'
                    board[{x}][{y}] = '.' & (board[{x-2}][{y}] = {'@', '+'}) & board[{x-1}][{y}] = '$' & next(action) = d : '*';
                    
                    -- if board[x][y] is '-' and board[x][y+2] is '@' or '+' and board[x][y+1] is '$' or '*', and next(action) is 'l' then it becomes '$'
                    board[{x}][{y}] = '-' & (board[{x}][{y+2}] = {'@', '+'}) & board[{x}][{y+1}] = '$' & next(action) = l : '$';
                    
                    -- if board[x][y] is '.' and board[x][y+2] is '@' or '+' and board[x][y+1] is '$' or '*', and next(action) is 'l' then it becomes '$'
                    board[{x}][{y}] = '.' & (board[{x}][{y+2}] = {'@', '+'}) & board[{x}][{y+1}] = '$' & next(action) = l : '*';
                    
                esac;
            """

    # TODO: should add more box movement constraints here (e.g., preventing two-box pushes and box-wall collisions)

    return smv_state



def is_position_a_goal(board_data, x, y):
    if (x, y) in board_data['goals']:
        return "TRUE"
    return "FALSE"



# def generate_smv_win_spec(board_data):
#     """Encodes the LTL win condition in SMV syntax.
#
#     Returns:
#         String containing the SMV specification
#     """
#     num_boxes = len(board_data['boxes'])
#     box_on_goal_conditions = [f"box{i + 1}_on_goal" for i in range(num_boxes)]
#     win_condition = " & ".join(box_on_goal_conditions)
#
#     smv_win_spec = f"AG (!{win_condition})"  # should consider AG instead of F
#     return smv_win_spec


def main():
    xsb_board = """
------
#-.--#
#-$--#
#-@#-#
------
"""  # Example board

    board_data, keeper_x, keeper_y = parse_board(xsb_board)

    smv_model = f"""
    MODULE main 
    VAR
       {generate_smv_var(board_data, keeper_x, keeper_y)}

    ASSIGN
       {generate_smv_state(board_data, keeper_x, keeper_y)} 

    SPEC
    AG !(
        CASE
            TRUE : { '$' } notin board
            TRUE : TRUE
        ESAC
    )
 
    """

    with open("sokoban_model.smv", "w") as f:
        f.write(smv_model)


if __name__ == "__main__":
    main()
