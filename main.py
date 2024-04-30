import subprocess
import time

def generate_smv_file():
    # Run the Python script to generate the SMV file
    subprocess.run(["python", "generate_sokoban_smv.py"])

def generate_actions_file():
    # Run the Python script to generate the actions file
    subprocess.run(["python", "movesGen.py"])

def run_nusmv(file_path, solver_engine, output_file):
    with open(output_file, 'w') as f:
        start_time = time.time()
        process = subprocess.Popen(["./NuSMV", file_path], stdout=f, stderr=subprocess.STDOUT)
        _, _ = process.communicate()
        end_time = time.time()
        execution_time = end_time - start_time
    return execution_time

if __name__ == "__main__":
    # Generate the SMV file
    generate_smv_file()

    smv_file_path = "sokoban.smv"
    execution_time = run_nusmv(smv_file_path, "sat", "moves.txt")
    generate_actions_file()
    print("NuSMV Execution Time:", execution_time, "seconds")
