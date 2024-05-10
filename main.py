import os
import subprocess
import time

def generate_smv_file(board_file):
    iterative = str(0)
    index = str(1)
    # Run the Python script to generate the SMV file
    subprocess.run(["python", "generate_sokoban_smv.py", iterative, index, board_file])

def iterative_solution(board_file):
    subprocess.run(["python", "generate_skoboan_iterative_smv.py", board_file])

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



if __name__ == "__main__":

    # Part 2
    start_time = time.time()
    generate_smv_file("board4.txt")
    execution_time = run_nuXmv("commands_list.sh", "moves.txt")
    generate_actions_file()
    print("NuXmv Execution Time:", execution_time, "seconds")



    # Part 3
    # iterative_solution("board4.txt")
