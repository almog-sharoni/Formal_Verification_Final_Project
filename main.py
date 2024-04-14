def parse_board(xsb_input):
    """Parses the XSB representation.

    Returns:
       A dictionary containing:
           - wk_pos: (x, y) tuple of warehouse keeper position
           - boxes: List of (x, y) box positions
           - goals: List of (x, y) goal positions
           - walls: List of (x, y) wall positions
    """
    board_data = {
        'width': None,  # New!
        'height': None,  # New!
        'wk_pos': None,
        'boxes': [],
        'goals': [],
        'walls': [],
        'floors': []
    }

    lines = xsb_input.strip().splitlines()
    board_data['width'] = len(lines[0])
    board_data['height'] = len(lines)
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '@':
                board_data['wk_pos'] = (x, y)
            elif char == '$':
                board_data['boxes'].append((x, y))
            elif char == '.':
                board_data['goals'].append((x, y))
            elif char == '#':  # New!
                board_data['walls'].append((x, y))
            elif char == '+':  # New!
                board_data['wk_pos'] = (x, y)
                board_data['goals'].append((x, y))
            elif char == '*':  # New!
                board_data['boxes'].append((x, y))
                board_data['goals'].append((x, y))
            elif char == '-':  # New!
                board_data['floors'].append((x, y))

    wall_array = []
    for line in xsb_input.strip().splitlines():
        row = []
        for char in line:
            row.append("TRUE" if char == '#' else "FALSE")
        wall_array.append(row)

    goals_array = []
    for line in xsb_input.strip().splitlines():
        row = []
        for char in line:
            row.append("TRUE" if char in ['.', '*'] else "FALSE")
        goals_array.append(row)

    # boxes_array = []
    # for line in xsb_input.strip().splitlines():
    #     row = []
    #     for char in line:
    #         row.append("TRUE" if char in ['$', '*'] else "FALSE")
    #     boxes_array.append(row)

    floor_array = []
    for line in xsb_input.strip().splitlines():
        row = []
        for char in line:
            row.append("TRUE" if char == '-' else "FALSE")
        floor_array.append(row)

    # board_data['walls'] = wall_array  # Add to the board_data dictionary

    board_data['walls'] = wall_array
    board_data['goals'] = goals_array
    # board_data['boxes'] = boxes_array
    board_data['floors'] = floor_array

    return board_data

def add_square_padding_lists(board, padding_width=2, padding_value="TRUE"):
    """Adds padding of a specified width around a 2D boolean list of lists.

    Args:
        board: The 2D boolean array as a list of lists.
        padding_width: The width of the padding on each side (default: 1).
        padding_value: The boolean value to use for padding (default: False).

    Returns:
        A new 2D boolean list of lists with the added padding.
    """

    new_board = []
    height = len(board)

    # Add top padding
    for _ in range(padding_width):
        new_board.append([padding_value] * (len(board[0]) + 2 * padding_width))

    # Add original rows with side padding
    for row in board:
        new_row = [padding_value] * padding_width + row + [padding_value] * padding_width
        new_board.append(new_row)

    # Add bottom padding
    for _ in range(padding_width):
        new_board.append([padding_value] * (len(board[0]) + 2 * padding_width))

    return new_board


def generate_smv_define(board_data):
    columns = board_data['width']
    rows = board_data['height']

    smv_define = f"""
        rows := {rows};
        columns := {columns};
       
        """

    return smv_define


def generate_smv_state(board_data):
    grid_width = board_data['width']
    grid_height = board_data['height']
    num_boxes = len(board_data['boxes'])
    wk_x, wk_y = board_data['wk_pos']

    smv_state = f"""
    
        wk_x : 0..{grid_width - 1}; 
        wk_y : 0..{grid_height - 1}; 
        """

    for i in range(num_boxes):
        smv_state += f"""
        box{i + 1}_x : 0..{grid_width - 1};
        box{i + 1}_y : 0..{grid_height - 1};
        box{i + 1}_on_goal : boolean; 
        """

    smv_state += f"""
        walls : array 0..{len(board_data['walls'][0])} of array 0..{len(board_data['walls'][1])} of boolean; 
        
        goals : array 0..{len(board_data['goals'][0])} of array 0..{len(board_data['goals'][1])} of boolean;
        
        floors : array 0..{len(board_data['floors'][0])} of array 0..{len(board_data['floors'][1])} of boolean;

    
        action : {{up, down, left, right,0}};  

    """



    smv_state += f"""
    ASSIGN 
        init(wk_x) := {wk_x};
        init(wk_y) := {wk_y};
        init(action) := 0;
        """

    for i in range(num_boxes):
        smv_state += f"""
        init(box{i + 1}_x) := {board_data['boxes'][i][0]};  
        init(box{i + 1}_y) := {board_data['boxes'][i][1]};
        init(box{i + 1}_on_goal) := {is_position_a_goal(board_data, board_data['boxes'][i][0], board_data['boxes'][i][1])}; 
        """

    # for x in range(grid_width):
    #     for y in range(grid_height):
    #         # print("index", x, y)
    #         smv_state += f"""
    #             init(walls[{x}][{y}]) := {board_data['walls'][x][y]};
    #             init(goals[{x}][{y}]) := {board_data['goals'][x][y]};
    #             init(floors[{x}][{y}]) := {board_data['floors'][x][y]};
    #             """

    smv_state += init_board_list(board_data['walls'], 'walls')
    smv_state += init_board_list(board_data['goals'], 'goals')
    smv_state += init_board_list(board_data['floors'], 'floors')

    # Movement Constraints (Iterative)
    smv_state += f"""
    next(walls) := walls;  -- Walls do not change
    next(goals) := goals;  -- Goals do not change
    next(floors) := floors;  -- Floors do not change
     
     next(wk_x) := 
            case
                wk_x = 0 : wk_x;  -- Left edge
                wk_x = {grid_width - 1} : wk_x;  -- Right edge
               
                action = left & !walls[wk_x - 1][wk_y] : wk_x - 1;   -- Can move right if no wall to the right
                action = right & !walls[wk_x + 1][wk_y] : wk_x + 1;  -- Can move left if no wall to the left
                            
                TRUE : wk_x;  -- Default: stay in the same position if no valid move
            esac;

        next(wk_y) :=  
            case
                wk_y = 0 : wk_y;  -- Top edge
                wk_y = {grid_height - 1} : wk_y;  -- Bottom edge     
                         
                action = up & !walls[wk_x][wk_y - 1] : wk_y - 1;  -- Can move up if no wall below
                action = down & !walls[wk_x][wk_y + 1] : wk_y + 1;  -- Can move down if no wall above
                
                TRUE : wk_y;   -- Default: stay in the same position if no valid move
            esac;
    """

    for i in range(num_boxes):
        smv_state += f"""
         next(box{i + 1}_x) := 
             case
                 box{i + 1}_x = 0 : box{i + 1}_x;  -- Left edge
                 box{i + 1}_x = {grid_width - 1} : box{i + 1}_x;  -- Right edge

                 --action = left  & !walls[box{i + 1}_x - 1][box{i + 1}_y] & wk_x = box{i + 1}_x + 1 & wk_y = box{i + 1}_y : box{i + 1}_x - 1;  -- Space to push
                 --action = right  & !walls[box{i + 1}_x + 1][box{i + 1}_y] & wk_x = box{i + 1}_x - 1 & wk_y = box{i + 1}_y : box{i + 1}_x + 1;  -- Space to push
                 
                action = left & (next(wk_x) = box{i + 1}_x & next(wk_y) = box{i + 1}_y) : box{i + 1}_x - 1;  -- Warehouse keeper is pushing box {i + 1}
                action = right & (next(wk_x) = box{i + 1}_x & next(wk_y) = box{i + 1}_y) : box{i + 1}_x + 1;  -- Warehouse keeper is pushing box {i + 1}
                 TRUE : box{i + 1}_x;  -- Default: no movement
             esac;

         next(box{i + 1}_y) := 
             case
                 box{i + 1}_y = 0 : box{i + 1}_y;  -- Top edge
                 box{i + 1}_y = {grid_height - 1} : box{i + 1}_y;  -- Bottom edge 
                 
                 --action = down  & !walls[box{i + 1}_x][box{i + 1}_y + 1] & wk_x = box{i + 1}_x & wk_y = box{i + 1}_y - 1 : box{i + 1}_y + 1;  -- Space to push
                 --action = up  & !walls[box{i + 1}_x][box{i + 1}_y - 1] & wk_x = box{i + 1}_x & wk_y = box{i + 1}_y + 1 : box{i + 1}_y - 1;  -- Space to push
                 
                action = down & (next(wk_x) = box{i + 1}_x & next(wk_y) = box{i + 1}_y) : box{i + 1}_y + 1;  -- Warehouse keeper is pushing box {i + 1}
                action = up & (next(wk_x) = box{i + 1}_x & next(wk_y) = box{i + 1}_y) : box{i + 1}_y - 1;  -- Warehouse keeper is pushing box {i + 1}
                
                 TRUE : box{i + 1}_y;  -- Default: no movement
             esac;
             
        next(box{i + 1}_on_goal) :=
        case
            goals[next(box{i + 1}_x)][next(box{i + 1}_y)] : TRUE;
            TRUE : FALSE;  -- Default: not on goal
        esac;
        """
    # TODO: should add more box movement constraints here (e.g., preventing two-box pushes and box-wall collisions)

    return smv_state


def init_board_list(list,list_name):
    init_walls = ""
    for x in range(len(list)):
        for y in range(len(list[x])):
            init_walls += f"""
            init({list_name}[{x}][{y}]) := {list[x][y]};"""
    return init_walls


def is_position_a_goal(board_data, x, y):
    if (x, y) in board_data['goals']:
        return "TRUE"
    return "FALSE"


def generate_smv_actions(board_data):
    grid_width = board_data['width']  # Access grid dimensions
    grid_height = board_data['height']

    smv_actions = f"""
        next(action) = up | next(action) = down | next(action) = right | next(action) = left;  -- Non-deterministic choice of action
"""

    return smv_actions


def generate_smv_win_spec(board_data):
    """Encodes the LTL win condition in SMV syntax.

    Returns:
        String containing the SMV specification
    """
    num_boxes = len(board_data['boxes'])
    box_on_goal_conditions = [f"box{i + 1}_on_goal" for i in range(num_boxes)]
    win_condition = " & ".join(box_on_goal_conditions)

    smv_win_spec = f"AG (!{win_condition})"  # should consider AG instead of F
    return smv_win_spec


def main():
    xsb_board = """
------
#-.--#
#-$--#
#-@#-#
------
"""  # Example board

    board_data = parse_board(xsb_board)

    smv_model = f"""
    MODULE main 
    VAR
       {generate_smv_state(board_data)}

    TRANS
       {generate_smv_actions(board_data)} 

    SPEC
       {generate_smv_win_spec(board_data)}
    """

    with open("sokoban_model.smv", "w") as f:
        f.write(smv_model)


if __name__ == "__main__":
    main()
