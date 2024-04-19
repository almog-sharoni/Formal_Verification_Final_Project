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
        --Cell: {"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL", "BOX_ON_GOAL", "WALL", "FLOOR"};

        --board : array 0..{rows - 1} of array 0..{columns - 1} of Cell;

        -- board : array 0..{rows - 1} of array 0..{columns - 1} of {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL", "#", "FLOOR", "BOX_ON_GOAL"}}; 
        board : array -2..rows+1 of array -2..columns+1 of {{"KEEPER", "BOX", "GOAL", "KEEPER_ON_GOAL","WALL" , "FLOOR", "BOX_ON_GOAL", "NULL"}};  

        keeper_x : 0..rows_minus_one;
        keeper_y : 0..columns_minus_one;

        action : {{u, d, l, r, 0}};  

    '''

    return smv_var


def generate_smv_state(board, keeper_x, keeper_y):
    rows = len(board)
    columns = len(board[0])

    smv_state = f''' 
            init(action) := 0;
            init(keeper_x) := {keeper_x};
            init(keeper_y) := {keeper_y};

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
    smv_state += f'''
            next(keeper_x) := case
                (action = u) & keeper_x > 0 & (board[keeper_x - 1][keeper_y] = FLOOR | board[keeper_x - 1][keeper_y] = GOAL): keeper_x - 1;
                -- (action = u) & keeper_x > 1 & (board[keeper_x - 1][keeper_y] = "BOX" | board[keeper_x - 1][keeper_y] = "BOX_ON_GOAL") & (board[keeper_x - 2][keeper_y] = "FLOOR" | board[keeper_x - 2][keeper_y] = "GOAL") : keeper_x - 1
                (action = d) & keeper_x < rows - 1 & (board[keeper_x + 1][keeper_y] = FLOOR | board[keeper_x + 1][keeper_y] = GOAL): keeper_x + 1;
                -- (action = d) & keeper_x < rows - 2 & (board[keeper_x + 1][keeper_y] = "BOX" | board[keeper_x + 1][keeper_y] = "BOX_ON_GOAL") & (board[keeper_x + 2][keeper_y] = "FLOOR" | board[keeper_x + 2][keeper_y] =  "GOAL"): keeper_x + 1;
                TRUE: keeper_x;


            esac;

            next(keeper_y) := case
                (action = l) & keeper_y > 0 & (board[keeper_x][keeper_y - 1] = FLOOR | board[keeper_x][keeper_y - 1] = GOAL): keeper_y - 1;
                -- (action = l) &  keeper_y > 1 & (board[keeper_x][keeper_y - 1] = "BOX" | board[keeper_x][keeper_y - 1] = "BOX_ON_GOAL") & (board[keeper_x][keeper_y - 2] = "FLOOR" | board[keeper_x][keeper_y - 2] = "GOAL"): keeper_y - 1;
                (action = r) & keeper_y < columns - 1 & (board[keeper_x][keeper_y + 1] = FLOOR | board[keeper_x][keeper_y + 1] = GOAL): keeper_y + 1;
                -- (action = r) & keeper_y < columns - 2 & (board[keeper_x][keeper_y + 1] = "BOX" | board[keeper_x][keeper_y + 1] =  "BOX_ON_GOAL") & (board[keeper_x][keeper_y + 2] = "FLOOR" | board[keeper_x][keeper_y + 2] = "GOAL") : keeper_y + 1;
                TRUE: keeper_y;
            esac;

            next(board) :=
                case
                    (action = u) & keeper_x > 0 & (board[keeper_x - 1][keeper_y] = BOX | board[keeper_x - 1][keeper_y] = BOX_ON_GOAL) & (board[keeper_x - 2][keeper_y] = FLOOR | board[keeper_x - 2][keeper_y] = GOAL):
                    (case
                        board[keeper_x - 2][keeper_y] = FLOOR: (board[keeper_x - 2][keeper_y] := BOX; board[keeper_x - 1][keeper_y] := (board[keeper_x - 1][keeper_y] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        board[keeper_x - 2][keeper_y] = GOAL: (board[keeper_x - 2][keeper_y] := BOX_ON_GOAL; board[keeper_x - 1][keeper_y] := (board[keeper_x - 1][keeper_y] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        TRUE: board;
                    esac);

                    (action = d) & keeper_x < rows - 1 & (board[keeper_x + 1][keeper_y] = BOX | board[keeper_x + 1][keeper_y] = BOX_ON_GOAL) & (board[keeper_x + 2][keeper_y] = FLOOR | board[keeper_x + 2][keeper_y] = GOAL):
                    (case
                        board[keeper_x + 2][keeper_y] = FLOOR: (board[keeper_x + 2][keeper_y] := BOX; board[keeper_x + 1][keeper_y] := (board[keeper_x + 1][keeper_y] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        board[keeper_x + 2][keeper_y] = GOAL: (board[keeper_x + 2][keeper_y] := BOX_ON_GOAL; board[keeper_x + 1][keeper_y] := (board[keeper_x + 1][keeper_y] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        TRUE: board;
                    esac);

                    (action = l) & keeper_y > 0 & (board[keeper_x][keeper_y - 1] = BOX | board[keeper_x][keeper_y - 1] = BOX_ON_GOAL) & (board[keeper_x][keeper_y - 2] = FLOOR | board[keeper_x][keeper_y - 2] = GOAL):
                    (case
                        board[keeper_x][keeper_y - 2] = FLOOR: (board[keeper_x][keeper_y - 2] := BOX; board[keeper_x][keeper_y - 1] := (board[keeper_x][keeper_y - 1] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        board[keeper_x][keeper_y - 2] = GOAL: (board[keeper_x][keeper_y - 2] := BOX_ON_GOAL; board[keeper_x][keeper_y - 1] := (board[keeper_x][keeper_y - 1] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        TRUE: board;
                    esac);

                    (action = r) & keeper_y < columns - 1 & (board[keeper_x][keeper_y + 1] = BOX | board[keeper_x][keeper_y + 1] = BOX_ON_GOAL) & (board[keeper_x][keeper_y + 2] = FLOOR | board[keeper_x][keeper_y + 2] = GOAL):
                    (case
                        board[keeper_x][keeper_y + 2] = FLOOR: (board[keeper_x][keeper_y + 2] := BOX; board[keeper_x][keeper_y + 1] := (board[keeper_x][keeper_y + 1] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        board[keeper_x][keeper_y + 2] = GOAL: (board[keeper_x][keeper_y + 2] := BOX_ON_GOAL; board[keeper_x][keeper_y + 1] := (board[keeper_x][keeper_y + 1] = BOX_ON_GOAL) ? KEEPER_ON_GOAL: KEEPER); board[keeper_x][keeper_y] := (board[keeper_x][keeper_y] = KEEPER_ON_GOAL) ? GOAL: FLOOR;
                        TRUE: board;
                    esac);
                TRUE: board;
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
    DEFINE
        {generate_smv_define(board_data)}
    VAR
        {generate_smv_var(board_data)}

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
