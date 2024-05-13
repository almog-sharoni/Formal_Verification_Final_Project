import os
import subprocess
import sys
import time


def generate_actions_file():
    subprocess.run(["python", "movesGen.py"])

def run_nuXmv(file_path, output_file):
    with open(output_file, 'w') as f:
        start_time = time.time()
        process = subprocess.Popen(["./NuXmv", "-source", file_path], stdout=f, stderr=subprocess.STDOUT)
        _, _ = process.communicate()
        end_time = time.time()
        execution_time = end_time - start_time
    return execution_time

def read_board_into_file(i):
    with open("moves.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if "rows" in line:
                rows = int(line[11:])
            if "columns" in line:
                columns = int(line[14:])
        board = [[0 for _ in range(columns)] for _ in range(rows)]
    start_processing = False

    with open("moves.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if "specification" in line:
                start_processing = True
                continue  # Skip processing this line
            if start_processing:
                if "WALL" in line:
                    board[int(line[10])][int(line[13])] = '#'
                if "BOX" in line:
                    board[int(line[10])][int(line[13])] = '$'
                if "KEEPER" in line:
                    board[int(line[10])][int(line[13])] = '@'
                if "GOAL" in line:
                    board[int(line[10])][int(line[13])] = '.'
                if "BOX_ON_GOAL" in line:
                    board[int(line[10])][int(line[13])] = '*'
                if "KEEPER_ON_GOAL" in line:
                    board[int(line[10])][int(line[13])] = '+'
                if "FLOOR" in line:
                    board[int(line[10])][int(line[13])] = '-'

    with open(f"board_iterative{i}.txt", "w") as file:
        for row in board:
            for cell in row:
                file.write(str(cell))
            file.write("\n")

    return "board_iterative" + str(i) + ".txt"

def goals_number(board_file):
    goals = []
    with open(board_file, "r") as file:
        # Iterate over each line in the file
        for row_index, line in enumerate(file):
            # Iterate over each character in the line
            for col_index, char in enumerate(line.strip()):
                # Check if the character is '$' or '*'
                if char in ".*":
                    # Add the position (row_index, col_index) to the list
                    goals.append((row_index, col_index))
    return len(goals)

def generate_iterative_smv_files(board_file):
    numbers_of_goals = goals_number(board_file)
    iterative = str(1)
    index = str(1)
    total_execution_time = 0
    for i in range(numbers_of_goals):
        # Run the Python script to generate the SMV file
        subprocess.run(["python", "generate_sokoban_smv.py", iterative, index, board_file])
        execution_time = run_nuXmv("commands_list.sh", "moves.txt")
        print()
        print("NuXmv Execution Time for board_iterative" + str(i) + ".txt:", execution_time, "seconds")
        generate_actions_file()
        board_file = read_board_into_file(int(index))
        if os.path.exists("moves.txt"):
            os.remove("moves.txt")
        total_execution_time += execution_time
        print("****************************************************")
        print("****************************************************")
        print()
        index = str(int(index) + 1)

    print("Total Execution Time:", total_execution_time, "seconds")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_sokoban_iterative_smv.py param1")
        sys.exit(1)
    board_file = sys.argv[1]
    generate_iterative_smv_files(board_file)