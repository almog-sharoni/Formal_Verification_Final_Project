import subprocess
import time

def generate_smv_file():
    # Run the Python script to generate the SMV file
    subprocess.run(["python", "generate_sokoban_smv.py"])

def generate_iterative_smv_file():
    # Run the Python script to generate the SMV file
    subprocess.run(["python", "generate_skoboan_iterative_smv.py"])
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
    # Generate the SMV file
    # generate_smv_file()
    # execution_time = run_nuXmv("commands_list.sh", "moves.txt")


    # # print move.txt
    # with open("moves.txt", "r") as file:
    #     lines = file.readlines()
    #     for line in lines:
    #         print(line)


    generate_iterative_smv_file()
    execution_time = run_nuXmv("commands_list_iterative.sh", "moves.txt")


    generate_actions_file()
    print("NuXmv Execution Time:", execution_time, "seconds")
