import re
import subprocess
import os
from itertools import product
from math import prod

# File path of the source file
file_path = "prefetcher/pythia.l1d_pref"

base_ipc = [0.628204,0.255851]

# Variables and their possible values for hyperparameter tuning
hyperparameters = {
    "ratio1": [-0.4,-0.6,-0.8,-1],
    "ratio2": [-0.1,-0.2,-0.4,-0.6,-0.8,-1],
}

hyperparameters1 = {
    "PREFETCH_DEGREE": [3, 4, 5, 6],
    "NUM_DELTAS": [3, 4, 5, 6],
}

# Commands to run for each iteration
commands = [
    "bin/pythia-no-1core -warmup_instructions 50000000 -simulation_instructions 50000000 -traces ../PARSEC/parsec_2.1.blackscholes.simlarge.prebuilt.drop_1750M.length_250M.champsimtrace.xz",
    "bin/pythia-no-1core -warmup_instructions 50000000 -simulation_instructions 50000000 -traces ../PARSEC/parsec_2.1.canneal.simlarge.prebuilt.drop_1250M.length_250M.champsimtrace.xz",
]

# Backup the original file
backup_path = file_path + ".bak"
if not os.path.exists(backup_path):
    os.rename(file_path, backup_path)

# Function to modify a specific variable in the file
def modify_macro(file_content, macro, new_value):
    pattern = rf"(#define\s+{macro}\s+)([-+]?\d*\.\d+|\d+)"  # Match both floats and integers
    replacement = rf"#define {macro} {new_value}"
    modified_content, count = re.subn(pattern, replacement, file_content, flags=re.MULTILINE)
    if count == 0:
        print(f"Warning: {macro} not found in file.")
    return modified_content

# Function to parse IPC from command output
def parse_ipc(output):
    match = re.search(r"CPU 0 cumulative IPC:\s+(\d+\.\d+)", output)
    if match:
        return float(match.group(1))
    return None

# Run experiments for given hyperparameter combinations and return best config based on geometric mean IPC
def run_experiments(hyperparams):
    combinations = list(product(*hyperparams.values()))
    best_config = None
    best_geo_mean_speedup = 0.0

    for i, combo in enumerate(combinations):
        print(f"\nRunning experiment {i + 1}/{len(combinations)} with params: {combo}")
        
        # Read the original file content
        with open(backup_path, "r") as file:
            content = file.read()
        
        # Update the file with the current combination
        for var, value in zip(hyperparams.keys(), combo):
            content = modify_macro(content, var, value)
        
        # Save the modified content back to the file
        with open(file_path, "w") as file:
            file.write(content)
        
        # Verify content modification (debugging step)
        #print(f"Updated content for {combo}:\n{content}")

        # Compile the program
        try:
            print("Compiling with ./build_champsim.sh pythia no 1...")
            subprocess.run("./build_champsim.sh pythia no 1", shell=True, check=True, capture_output=True, text=True)
            print("Compilation successful.")
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e.stderr}")
            continue

        ipc_values = []
        # Run the specified commands and gather IPC values
        for j, command in enumerate(commands, start=1):
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
                ipc = parse_ipc(result.stdout)
                if ipc is not None:
                    ipc_values.append(ipc)
                else:
                    print(f"Failed to parse IPC for command {command}")
            except subprocess.CalledProcessError as e:
                print(f"Error running command {command}: {e.stderr}")
                continue

        # Calculate geometric mean of IPCs
        if len(ipc_values) == len(commands):

            speedup = [ ipc_values[i]/base_ipc[i] for i in range(len(ipc_values)) ]
            geo_mean_speedup =  prod(speedup) ** ( 1/len(ipc_values))

            print(f"Geometric mean IPC for {combo}: {geo_mean_speedup}, speedup values are {speedup} ")

            if geo_mean_speedup > best_geo_mean_speedup:
                best_geo_mean_speedup = geo_mean_speedup
                best_config = combo
        else:
            print(f"Skipping configuration due to missing IPC values: {combo}")

    print(f"\nBest configuration for hyperparameters: {best_config} with IPC {best_geo_mean_speedup}")
    return best_config

# Run experiments for hyperparameters and get the best config
best_config = run_experiments(hyperparameters)

# Update the source file with the best configuration from hyperparameters for hyperparameters1 iteration
with open(backup_path, "r") as file:
    content = file.read()

for var, value in zip(hyperparameters.keys(), best_config):
    content = modify_macro(content, var, value)

with open(file_path, "w") as file:
    file.write(content)
with open(backup_path, "w") as file:
    file.write(content)

# Run experiments for hyperparameters1 using the best configuration from hyperparameters
best_config_hyper1 = run_experiments(hyperparameters1)

# Restore the original file
os.rename(backup_path, file_path)
print("\nExperiments completed and file restored to its original state.")
print(f"Final best configuration for hyperparameters1: {best_config_hyper1}")
