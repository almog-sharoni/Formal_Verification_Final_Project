# @ - keeper
# + - keeper on goal
# $ - box
# * - box on goal
# # - wall
# . - goal
# - - floor
def parse_board(xsb_input):
    board_array = []
    for row in xsb_input.strip().splitlines():
        row_array = []
        for cell in row:
            if cell == "@":
                row_array.append("KEEPER")
            if cell == "+":
                row_array.append("KEEPER_ON_GOAL")
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

    return board_array


def generate_smv_define(board):
    smv_define = f'''
        rows := {len(board)};
        columns := {len(board[0])};
        rows_minus_one := rows - 1;
        columns_minus_one := columns - 1;

        '''

    return smv_define


def generate_smv_var(board):
    rows = len(board)
    columns = len(board[0])

    print("rows: ", rows)
    print("columns: ", columns)

    smv_var = f'''
        -- Cell: {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL", "BOX_ON_GOAL", "WALL", "FLOOR", "NULL"}};

        -- board : array -2..rows+1 of array -2..columns+1 of Cell;

        -- board : array 0..{rows - 1} of array 0..{columns - 1} of {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL", "#", "FLOOR", "BOX_ON_GOAL"}}; 
        board : array -2..rows+1 of array -2..columns+1 of {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL","WALL" , "FLOOR", "BOX_ON_GOAL", "NULL"}};  

        action : {{u, d, l, r, 0}};  
        
        box_on_goal : boolean;

    '''

    return smv_var


def generate_smv_state(board):
    rows = len(board)
    columns = len(board[0])

    smv_state = f''' 
            init(action) := 0;
            '''
    smv_state += f'''
            -- padding in 'NULL' the values outside the board

            '''
    for x in range(-2, rows + 2):
        for y in range(-2, columns + 2):
            if x < 0 or y < 0 or x >= rows or y >= columns:
                smv_state += f'''
                       init(board[{x}][{y}]) := "NULL";
                   '''
            else:
                smv_state += f'''
                       init(board[{x}][{y}]) := "{board[x][y]}";
                   '''

    goals = []
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == "GOAL" or board[x][y] == "BOX_ON_GOAL":
                goals.append((x, y))
                print("goal: ", goals)

    smv_state += f'''

        -- dont need to refer the borders as we have walls
        next(action) := {{u, d, l, r}};
        
        next(box_on_goal) := case
            board[{goals[0][0]}][{goals[0][1]}] = "BOX_ON_GOAL" : TRUE;
            TRUE : FALSE;
        esac;
        
        

        '''

    for x in range(-2, rows + 2):
        for y in range(-2, columns + 2):
            if x < 0 or y < 0 or x >= rows or y >= columns:
                smv_state += f'''
        next(board[{x}][{y}]) := "NULL";
                       '''
            else:
                smv_state += f'''
        next(board[{x}][{y}]) := 
            case
                board[{x}][{y}] = "KEEPER_ON_GOAL": 
                    case
                        board[{x + 1}][{y}] = "FLOOR" & next(action) = d : "GOAL";
                        board[{x - 1}][{y}] = "FLOOR" & next(action) = u : "GOAL";
                        board[{x}][{y + 1}] = "FLOOR" & next(action) = r : "GOAL";
                        board[{x}][{y - 1}] = "FLOOR" & next(action) = l : "GOAL";
                        board[{x + 1}][{y}] = "BOX" & (board[{x + 2}][{y}] = "FLOOR" | board[{x + 2}][{y}] = "GOAL") & next(action) = d : "GOAL";
                        board[{x - 1}][{y}] = "BOX" & (board[{x - 2}][{y}] = "FLOOR" | board[{x - 2}][{y}] = "GOAL") & next(action) = u : "GOAL";
                        board[{x}][{y + 1}] = "BOX" & (board[{x}][{y + 2}] = "FLOOR" | board[{x}][{y + 2}] = "GOAL") & next(action) = r : "GOAL";
                        board[{x}][{y - 1}] = "BOX" & (board[{x}][{y - 2}] = "FLOOR" | board[{x}][{y - 2}] = "GOAL") & next(action) = l : "GOAL";
                        TRUE : "KEEPER_ON_GOAL";
                    esac;

                board[{x}][{y}] = "KEEPER":
                    case
                        board[{x + 1}][{y}] = "FLOOR" & next(action) = d : "FLOOR";
                        board[{x - 1}][{y}] = "FLOOR" & next(action) = u : "FLOOR";
                        board[{x}][{y + 1}] = "FLOOR" & next(action) = r : "FLOOR";
                        board[{x}][{y - 1}] = "FLOOR" & next(action) = l : "FLOOR";
                        board[{x + 1}][{y}] = "BOX" & (board[{x + 2}][{y}] = "FLOOR" | board[{x + 2}][{y}] = "GOAL") & next(action) = d : "FLOOR";
                        board[{x - 1}][{y}] = "BOX" & (board[{x - 2}][{y}] = "FLOOR" | board[{x - 2}][{y}] = "GOAL") & next(action) = u : "FLOOR";
                        board[{x}][{y + 1}] = "BOX" & (board[{x}][{y + 2}] = "FLOOR" | board[{x}][{y + 2}] = "GOAL") & next(action) = r : "FLOOR";
                        board[{x}][{y - 1}] = "BOX" & (board[{x}][{y - 2}] = "FLOOR" | board[{x}][{y - 2}] = "GOAL") & next(action) = l : "FLOOR";
                        TRUE : "KEEPER";
                    esac;

                board[{x}][{y}] = "FLOOR":
                    case
                        (board[{x + 1}][{y}] = "KEEPER" | board[{x + 1}][{y}] = "KEEPER_ON_GOAL") & next(action) = u : "KEEPER";
                        (board[{x - 1}][{y}] = "KEEPER" | board[{x - 1}][{y}] = "KEEPER_ON_GOAL") & next(action) = d : "KEEPER";
                        (board[{x}][{y + 1}] = "KEEPER" | board[{x}][{y + 1}] = "KEEPER_ON_GOAL") & next(action) = l : "KEEPER";
                        (board[{x}][{y - 1}] = "KEEPER" | board[{x}][{y - 1}] = "KEEPER_ON_GOAL") & next(action) = r : "KEEPER";
                        (board[{x + 2}][{y}] = "KEEPER" | board[{x + 2}][{y}] = "KEEPER_ON_GOAL") & (board[{x + 1}][{y}] = "BOX" | board[{x + 1}][{y}] = "BOX_ON_GOAL") & next(action) = u : "BOX";
                        (board[{x - 2}][{y}] = "KEEPER" | board[{x - 2}][{y}] = "KEEPER_ON_GOAL") & (board[{x - 1}][{y}] = "BOX" | board[{x - 1}][{y}] = "BOX_ON_GOAL") & next(action) = d : "BOX";
                        (board[{x}][{y + 2}] = "KEEPER" | board[{x}][{y + 2}] = "KEEPER_ON_GOAL") & (board[{x}][{y + 1}] = "BOX" | board[{x}][{y + 1}] = "BOX_ON_GOAL") & next(action) = l : "BOX";
                        (board[{x}][{y - 2}] = "KEEPER" | board[{x}][{y - 2}] = "KEEPER_ON_GOAL") & (board[{x}][{y - 1}] = "BOX" | board[{x}][{y - 1}] = "BOX_ON_GOAL") & next(action) = r : "BOX";
                        TRUE : "FLOOR";
                    esac;

                board[{x}][{y}] = "GOAL":
                    case
                        (board[{x + 1}][{y}] = "KEEPER" | board[{x + 1}][{y}] = "KEEPER_ON_GOAL") & next(action) = u : "BOX_ON_GOAL";
                        (board[{x - 1}][{y}] = "KEEPER" | board[{x - 1}][{y}] = "KEEPER_ON_GOAL") & next(action) = d : "BOX_ON_GOAL";
                        (board[{x}][{y + 1}] = "KEEPER" | board[{x}][{y + 1}] = "KEEPER_ON_GOAL") & next(action) = l : "BOX_ON_GOAL";
                        (board[{x}][{y - 1}] = "KEEPER" | board[{x}][{y - 1}] = "KEEPER_ON_GOAL") & next(action) = r : "BOX_ON_GOAL";
                        (board[{x + 2}][{y}] = "KEEPER" | board[{x + 2}][{y}] = "KEEPER_ON_GOAL") & (board[{x + 1}][{y}] = "BOX" | board[{x + 1}][{y}] = "BOX_ON_GOAL") & next(action) = u : "BOX_ON_GOAL";
                        (board[{x - 2}][{y}] = "KEEPER" | board[{x - 2}][{y}] = "KEEPER_ON_GOAL") & (board[{x - 1}][{y}] = "BOX" | board[{x - 1}][{y}] = "BOX_ON_GOAL") & next(action) = d : "BOX_ON_GOAL";
                        (board[{x}][{y + 2}] = "KEEPER" | board[{x}][{y + 2}] = "KEEPER_ON_GOAL") & (board[{x}][{y + 1}] = "BOX" | board[{x}][{y + 1}] = "BOX_ON_GOAL") & next(action) = l : "BOX_ON_GOAL";
                        (board[{x}][{y - 2}] = "KEEPER" | board[{x}][{y - 2}] = "KEEPER_ON_GOAL") & (board[{x}][{y - 1}] = "BOX" | board[{x}][{y - 1}] = "BOX_ON_GOAL") & next(action) = r : "BOX_ON_GOAL";
                        TRUE : "GOAL";
                    esac;

                board[{x}][{y}] = "BOX":
                    case
                        (board[{x + 1}][{y}] = "KEEPER" | board[{x + 1}][{y}] = "KEEPER_ON_GOAL") & (board[{x - 1}][{y}] = "FLOOR" | board[{x - 1}][{y}] = "GOAL") & next(action) = u : "KEEPER";
                        (board[{x - 1}][{y}] = "KEEPER" | board[{x - 1}][{y}] = "KEEPER_ON_GOAL") & (board[{x + 1}][{y}] = "FLOOR" | board[{x + 1}][{y}] = "GOAL") & next(action) = d : "KEEPER";
                        (board[{x}][{y + 1}] = "KEEPER" | board[{x}][{y + 1}] = "KEEPER_ON_GOAL") & (board[{x}][{y - 1}] = "FLOOR" | board[{x}][{y - 1}] = "GOAL") & next(action) = l : "KEEPER";
                        (board[{x}][{y - 1}] = "KEEPER" | board[{x}][{y - 1}] = "KEEPER_ON_GOAL") & (board[{x}][{y + 1}] = "FLOOR" | board[{x}][{y + 1}] = "GOAL") & next(action) = r : "KEEPER";
                        TRUE : "BOX";    
                    esac;

                board[{x}][{y}] = "BOX_ON_GOAL":
                    case
                        (board[{x + 1}][{y}] = "KEEPER" | board[{x + 1}][{y}] = "KEEPER_ON_GOAL") & (board[{x - 1}][{y}] = "FLOOR" | board[{x - 1}][{y}] = "GOAL") & next(action) = u : "KEEPER_ON_GOAL";
                        (board[{x - 1}][{y}] = "KEEPER" | board[{x - 1}][{y}] = "KEEPER_ON_GOAL") & (board[{x + 1}][{y}] = "FLOOR" | board[{x + 1}][{y}] = "GOAL") & next(action) = d : "KEEPER_ON_GOAL";
                        (board[{x}][{y + 1}] = "KEEPER" | board[{x}][{y + 1}] = "KEEPER_ON_GOAL") & (board[{x}][{y - 1}] = "FLOOR" | board[{x}][{y - 1}] = "GOAL") & next(action) = l : "KEEPER_ON_GOAL";
                        (board[{x}][{y - 1}] = "KEEPER" | board[{x}][{y - 1}] = "KEEPER_ON_GOAL") & (board[{x}][{y + 1}] = "FLOOR" | board[{x}][{y + 1}] = "GOAL") & next(action) = r : "KEEPER_ON_GOAL";
                        TRUE : "BOX_ON_GOAL";    
                    esac;


                TRUE : board[{x}][{y}];

            esac;
            '''

    # TODO: should add more box movement constraints here (e.g., preventing two-box pushes and box-wall collisions)

    return smv_state


def generate_smv_win_spec(board_data):
    # save goals locations in array to use it in the win condition
    goals = []
    for x in range(len(board_data)):
        for y in range(len(board_data[0])):
            if board_data[x][y] == "GOAL" or board_data[x][y] == "BOX_ON_GOAL":
                goals.append((x, y))
                print("goal: ", goals)

    smv_win_spec = f''' board[{goals[0][0]}][{goals[0][1]}] = "BOX_ON_GOAL" '''
    for i in range(1, len(goals)):
        smv_win_spec += f''' & board[{goals[i][0]}][{goals[i][1]}] = "BOX_ON_GOAL" '''

    return smv_win_spec


def main():
    xsb_board = '''
------
#-.--#
#-$--#
#-@#-#
------
'''  # Example board
    # Example board
    xsb_board = """
-.-
-$-
-@-
"""

    board_data = parse_board(xsb_board)
    initial_board = board_data
    smv_model = f'''
    MODULE main 
    DEFINE
        {generate_smv_define(board_data)}
    VAR
        {generate_smv_var(board_data)}

    ASSIGN
        {generate_smv_state(board_data)} 

    LTLSPEC
    F(X(!({generate_smv_win_spec(initial_board)})))

    '''

    with open("sokoban.smv", "w") as f:
        f.write(smv_model)


if __name__ == "__main__":
    main()
