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
        '''

    return smv_define


def generate_smv_var(board):
    smv_var = f'''
    
        board : array -2..rows+1 of array -2..columns+1 of {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL","WALL" , "FLOOR", "BOX_ON_GOAL", "NULL"}};  

        action : {{u, d, l, r, 0}};  

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
                if board[x][y] != "GOAL":
                    smv_state += f'''
                           init(board[{x}][{y}]) := "{board[x][y]}";
                       '''

    goals = []
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == "GOAL" or board[x][y] == "BOX_ON_GOAL":
                goals.append((x, y))
                # print("goal: ", goals)

    smv_state += f'''

        -- dont need to refer the borders as we have walls
        next(action) := {{u, d, l, r}};

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
                        (board[{x + 1}][{y}] = "KEEPER" | board[{x + 1}][{y}] = "KEEPER_ON_GOAL") & next(action) = u : "KEEPER_ON_GOAL";--logic problem was here!
                        (board[{x - 1}][{y}] = "KEEPER" | board[{x - 1}][{y}] = "KEEPER_ON_GOAL") & next(action) = d : "KEEPER_ON_GOAL";--logic problem was here!
                        (board[{x}][{y + 1}] = "KEEPER" | board[{x}][{y + 1}] = "KEEPER_ON_GOAL") & next(action) = l : "KEEPER_ON_GOAL";--logic problem was here!
                        (board[{x}][{y - 1}] = "KEEPER" | board[{x}][{y - 1}] = "KEEPER_ON_GOAL") & next(action) = r : "KEEPER_ON_GOAL"; --logic problem was here!
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

    return smv_state


def generate_smv_win_spec(board_data, iterative=False):
    # save goals locations in array to use it in the win condition
    goals = []
    for x in range(len(board_data)):
        for y in range(len(board_data[0])):
            if board_data[x][y] == "GOAL" or board_data[x][y] == "BOX_ON_GOAL":
                goals.append((x, y))
                # print("goal: ", goals)

    if iterative:
        smv_win_spec = []
        for i in range(0, len(goals)):
            smv_win_spec.append(f'''LTLSPEC G(!( board[{goals[i][0]}][{goals[i][1]}] = "BOX_ON_GOAL" )) ''')

    else:
        smv_win_spec = f'''LTLSPEC G(!( board[{goals[0][0]}][{goals[0][1]}] = "BOX_ON_GOAL" '''
        if len(goals) > 1:
            for i in range(1, len(goals)):
                smv_win_spec += f''' & board[{goals[i][0]}][{goals[i][1]}] = "BOX_ON_GOAL"'''
        smv_win_spec += f''' ))'''

    return smv_win_spec, goals

def read_board_from_file(file_path):
    with open(file_path, 'r') as file:
        xsb_board = file.read()
    return xsb_board

def main():
    xsb_board = read_board_from_file("board3.txt")
    print(xsb_board)
    board_data = parse_board(xsb_board)
    print(board_data)
    initial_board = board_data
    smv_model = f'''
    MODULE main 
    DEFINE
        {generate_smv_define(board_data)}
    VAR
        {generate_smv_var(board_data)}
    '''
    smv_win_spec, goals = generate_smv_win_spec(board_data, True)

    smv_model += f'''

    ASSIGN
        {generate_smv_state(board_data)} 

    '''

    for i in range(0, len(goals)):
        smv_model_add = f'''
          init(board[{goals[i][0]}][{goals[i][1]}]) := "GOAL";
        '''
        for j in range(0, len(goals)):
            if i != j:
                smv_model_add += f'''
                init(board[{goals[j][0]}][{goals[j][1]}]) := "NULL";
                '''
                smv_final = smv_model + smv_model_add + smv_win_spec[i]
        with open(f"sokoban{i}.smv", "w") as f:
            f.write(smv_final)

    with open("commands_list_iterative.sh", "w") as f:
        f.write(f"read_model -i sokoban0.smv\n")
        f.write("go\n")
        f.write("check_ltlspec\n")
        f.write("\n")

    for i in range(1, len(goals)):
        with open("commands_list_iterative.sh", "a") as f:
            f.write("reset\n")
            f.write(f"read_model -i sokoban{i}.smv\n")
            f.write("go\n")
            f.write("check_ltlspec\n")
            f.write("\n")

    with open("commands_list_iterative.sh", "a") as f:
        f.write("quit\n")



if __name__ == "__main__":
    main()
