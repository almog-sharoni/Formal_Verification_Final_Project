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
    board_data['width'] = max(len(line) for line in lines)
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

    boxes_array = []
    for line in xsb_input.strip().splitlines():
        row = []
        for char in line:
            row.append("TRUE" if char in ['$', '*'] else "FALSE")
        boxes_array.append(row)

    floor_array = []
    for line in xsb_input.strip().splitlines():
        row = []
        for char in line:
            row.append("TRUE" if char == '-' else "FALSE")
        floor_array.append(row)

    # board_data['walls'] = wall_array  # Add to the board_data dictionary

    padded_walls = add_square_padding_lists(wall_array)
    board_data['walls'] = padded_walls
    board_data['goals'] = goals_array
    board_data['boxes'] = boxes_array
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


def generate_smv_var(board_data):
    grid_width = board_data['width']
    grid_height = board_data['height']
    # num_boxes = len(board_data['boxes'])
    # keeper_y, wk_y = board_data['wk_pos']

    smv_var = f"""
        columns : 
        keeper_x : 0..{grid_width - 1}; 
        keeper_y : 0..{grid_height - 1}; 
        """

    # for i in range(num_boxes):
    #     smv_var += f"""
    #     box{i + 1}_x : 0..{grid_width - 1};
    #     box{i + 1}_y : 0..{grid_height - 1};
    #     box{i + 1}_on_goal : boolean;
    #     """

    smv_var += f"""
        boxes: array 0..{len(board_data['boxes'][0])} of array 0..{len(board_data['boxes'][1])} of boolean;
   
        walls : array 0..{len(board_data['walls'][0])} of array 0..{len(board_data['walls'][1])} of boolean; 
        
        goals : array 0..{len(board_data['goals'][0])} of array 0..{len(board_data['goals'][1])} of boolean;
        
        floors : array 0..{len(board_data['floors'][0])} of array 0..{len(board_data['floors'][1])} of boolean;

        action : {{u, d, l, r, 0}};  

    """

    return smv_var

def generate_smv_state(board_data):
    grid_width = board_data['width']
    grid_height = board_data['height']
    num_boxes = len(board_data['boxes'])
    keeper_x, keeper_y = board_data['wk_pos']

    smv_state = f"""
    ASSIGN 
        init(keeper_x) := {keeper_x};
        init(keeper_y) := {keeper_y};
        init(action) := 0;
        """

    for x in range(len(grid_width)):
        for y in range(len(grid_height)):
            smv_state += f"""
                init(walls[{x}][{y}]) := {board_data['walls'][x][y]};
                init(goals[{x}][{y}]) := {board_data['goals'][x][y]};
                init(boxes[{x}][{y}]) := {board_data['boxes'][x][y]};
                init(floors[{x}][{y}]) := {board_data['floors'][x][y]};
                """

    # for i in range(num_boxes):
    #     smv_state += f"""
    #     init(box{i + 1}_x) := {board_data['boxes'][i][0]};
    #     init(box{i + 1}_y) := {board_data['boxes'][i][1]};
    #     init(box{i + 1}_on_goal) := {is_position_a_goal(board_data, board_data['boxes'][i][0], board_data['boxes'][i][1])};
    #     """

    # smv_state += initWalls(board_data['walls'])

    # Movement Constraints (Iterative)
    smv_state += f"""
    
    -- dont need to refer the borders as we have walls
    next(command) := {{u, d, l, r, 0}};
  
    
    next(keeper_y) := case
            -- keeper_x = {grid_width - 1} : keeper_x; -- Cannot move right if at the right edge
            ((next(command) = u) & (boxes[keeper_x][keeper_y-1] = 1 & (floors[keeper_x][keeper_y-2] = 1 | goals[keeper_x][keeper_y-2] = 1))) : keeper_y - 1;  -- Can move up if there is a box above
            ((next(command) = u) & (floors[keeper_x][keeper_y-1] = 1 | goals[keeper_x][keeper_y-1] = 1)) : keeper_y - 1;  -- Can move up if there is floor or goal above
                
            ((next(command) = d) & (boxes[keeper_x][keeper_y+1] = 1 & (floors[keeper_x][keeper_y+2] = 1 | goals[keeper_x][keeper_y+2] = 1))): keeper_y + 1;  -- Can move down if there is a box below
            ((next(command) = d) & (floors[keeper_x][keeper_y+1] = 1 | goals[keeper_x][keeper_y+1] = 1)): keeper_y + 1;  -- Can move down if there is floor or goal below
                
            TRUE : keeper_y;  -- Default: stay in the same position if no valid move
    esac;

    next(keeper_x) :=  case
            ((next(command) = l) & (boxes[keeper_x-1][keeper_y] = 1 & (floors[keeper_x-2][keeper_y] = 1 | goals[keeper_x-2][keeper_y] = 1))): keeper_x - 1;  -- Can move left if there is a box to the left
            ((next(command) = l) & (floors[keeper_x-1][keeper_y] = 1 | goals[keeper_x-1][keeper_y] = 1)): keeper_x - 1;  -- Can move left if there is floor or goal to the left
                
            ((next(command) = r) & (boxes[keeper_x+1][keeper_y] = 1 & (floors[keeper_x+2][keeper_y] = 1 | goals[keeper_x+2][keeper_y] = 1))): keeper_x + 1;  -- Can move right if there is a box to the right
            ((next(command) = r) & (floors[keeper_x+1][keeper_y] = 1 | goals[keeper_x+1][keeper_y] = 1)): keeper_x + 1;  -- Can move right if there is floor or goal to the right
            
            TRUE : keeper_x;  -- Default: stay in the same position if no valid move
    esac;
    
    -- check if next position of keeper is a box 
    next(boxes) := case
        (boxes[next(keeper_x)][next(keeper_y)] = 1) & (next(command) = u) : boxe
    
    
    """

    for i in range(num_boxes):
        smv_state += f"""
         next(box{i + 1}_x) := 
             case
                 box{i + 1}_x = 0 : box{i + 1}_x;  -- Left edge
                 box{i + 1}_x = {grid_width - 1} : box{i + 1}_x;  -- Right edge

                 -- Check for a push by the warehouse keeper:
                 --wk_x = box{i + 1}_x - 1 & wk_y = box{i + 1}_y &
                 !walls[box{i + 1}_x + 1][box{i + 1}_y] : box{i + 1}_x + 1;  -- Space to push
                 
                 -- Check if box on goal:
                 --box{i + 1}_x = {board_data['goals'][i][0]} & box{i + 1}_y = {board_data['goals'][i][1]} : box{i + 1}_on_goal;
                 
                 TRUE : box{i + 1}_x;  -- Default: no movement
             esac;

         next(box{i + 1}_y) := 
             case
                 box{i + 1}_y = 0 : box{i + 1}_y;  -- Top edge
                 box{i + 1}_y = {grid_height - 1} : box{i + 1}_y;  -- Bottom edge 

                 -- Check for a push by the warehouse keeper:
                 --wk_y = box{i + 1}_y - 1 & wk_x = box{i + 1}_x &  
                 !walls[box{i + 1}_x][box{i + 1}_y + 1] : box{i + 1}_y + 1;  -- Space to push
                 
                 -- Check if box on goal:
                 --box{i + 1}_x = {board_data['goals'][i][0]} & box{i + 1}_y = {board_data['goals'][i][1]} : box{i + 1}_on_goal;

                 TRUE : box{i + 1}_y;  -- Default: no movement
             esac;
        """
    # TODO: should add more box movement constraints here (e.g., preventing two-box pushes and box-wall collisions)

    return smv_state


def initWalls(walls):
    init_walls = ""
    for x in range(len(walls)):
        for y in range(len(walls[x])):
            init_walls += f"""
            init(walls[{x}][{y}]) := {walls[x][y]};"""
    return init_walls


def is_position_a_goal(board_data, x, y):
    if (x, y) in board_data['goals']:
        return "TRUE"
    return "FALSE"


def generate_smv_actions(board_data):
    grid_width = board_data['width']  # Access grid dimensions
    grid_height = board_data['height']

    smv_actions = f"""
        next(action) = action;  -- Non-deterministic choice of action
"""
    #     case
    #         action = 'up' & !walls[wk_x][wk_y + 1] :
    #             next(wk_y) := wk_y + 1;
    #             {update_boxes('up', board_data, grid_width, grid_height)};  -- Trigger box movement logic
    #
    #         action = 'down' & !walls[wk_x][wk_y - 1] :
    #             next(wk_y) := wk_y - 1;
    #             {update_boxes('down', board_data, grid_width, grid_height)};
    #
    #         action = 'left' & !walls[wk_x - 1][wk_y] :
    #             next(wk_x) := wk_x - 1;
    #             {update_boxes('left', board_data, grid_width, grid_height)};
    #
    #         action = 'right' & !walls[wk_x + 1][wk_y] :
    #             next(wk_x) := wk_x + 1;
    #             {update_boxes('right', board_data, grid_width, grid_height)};
    #
    #         TRUE : TRUE;  -- Preserve state if no valid action
    #     esac
    # """
    return smv_actions


def update_boxes(direction, board_data, grid_width, grid_height):
    num_boxes = len(board_data['boxes'])
    box_updates = ""
    for i in range(num_boxes):
        box_updates += f"""
        case
            box{i + 1}_x = wk_x & box{i + 1}_y = wk_y :  -- Warehouse keeper is pushing box {i + 1}
                case
                    action = 'up' & !walls[box{i + 1}_x][box{i + 1}_y + 1] : 
                        next(box{i + 1}_y) := box{i + 1}_y + 1;
                    action = 'down' & !walls[box{i + 1}_x][box{i + 1}_y - 1] : 
                        next(box{i + 1}_y) := box{i + 1}_y - 1;
                    action = 'left' & !walls[box{i + 1}_x - 1][box{i + 1}_y] : 
                        next(box{i + 1}_x) := box{i + 1}_x - 1;
                    action = 'right' & !walls[box{i + 1}_x + 1][box{i + 1}_y] : 
                        next(box{i + 1}_x) := box{i + 1}_x + 1;
                    TRUE : TRUE;  -- Preserve box position if no valid push
                esac;
            TRUE : TRUE;  -- Preserve box position if not pushed
        esac;
        """

    return box_updates


def generate_smv_win_spec(board_data):
    """Encodes the LTL win condition in SMV syntax.

    Returns:
        String containing the SMV specification
    """
    num_boxes = len(board_data['boxes'])
    box_on_goal_conditions = [f"box{i + 1}_on_goal" for i in range(num_boxes)]
    win_condition = " & ".join(box_on_goal_conditions)

    smv_win_spec = f"F ({win_condition})"  # should consider AG instead of F
    return smv_win_spec


def main():
    xsb_board = """
-----
#-.-#
#- $-#
#-@#-#
-----
"""  # Example board

    board_data = parse_board(xsb_board)

    smv_model = f"""
    MODULE main
        DEFINE
            {generate_smv_define(board_data)}
        VAR
            {generate_smv_var(board_data)}
           {generate_smv_state(board_data)}
    
        TRANS
           {generate_smv_actions(board_data)} 
    
        LTLSPEC
           {generate_smv_win_spec(board_data)}
    """

    with open("sokoban_model.smv", "w") as f:
        f.write(smv_model)


if __name__ == "__main__":
    main()
