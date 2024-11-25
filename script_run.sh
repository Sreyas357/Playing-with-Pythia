#!/bin/bash


# ./build_champsim.sh no no 1 1

TRACE_FOLDER=$1                 # Folder containing all trace files
PREFETCHER_FILE=$2  # which prefetcher file to run
NUM_INSTRUCTIONS=$3

WARMUP_INSTRUCTIONS=$((NUM_INSTRUCTIONS * 1000000))
SIMULATION_INSTRUCTIONS=$((NUM_INSTRUCTIONS * 1000000))

./build_champsim.sh ${PREFETCHER_FILE} no 1 1  2> temp.txt 

# Paths to executables and trace folder
BASE_PREFETCHER_EXEC="./bin/no-no-1core -warmup_instructions ${WARMUP_INSTRUCTIONS} -simulation_instructions ${SIMULATION_INSTRUCTIONS}"   # Path to ChampSim with the base prefetcher
CUSTOM_PREFETCHER_EXEC="./bin/${PREFETCHER_FILE}-no-1core -warmup_instructions ${WARMUP_INSTRUCTIONS} -simulation_instructions ${SIMULATION_INSTRUCTIONS}" # Path to ChampSim with your custom prefetcher

OUTPUT_FOLDER="./outputs_$NUM_INSTRUCTIONS"                # Folder to store output files
OUTPUT_FOLDER1="./outputs_custom_$NUM_INSTRUCTIONS"                # Folder to store output files

# Create output folder if it doesn't exist
mkdir -p "$OUTPUT_FOLDER"
mkdir -p "$OUTPUT_FOLDER1"

# Initialize an array to store speedups
speedups=()

# Loop through each trace file in the trace folder
for trace in "$TRACE_FOLDER"/*; do
    # Get trace filename without path and extension
    trace_name=$(basename "$trace")
    
    # Run base prefetcher and store output
    base_output_file="$OUTPUT_FOLDER/${trace_name}_base.out"
    
    if [[ ! -f "$base_output_file" ]]; then
        eval " $BASE_PREFETCHER_EXEC -traces $trace > $base_output_file"
    fi
    base_ipc=$(grep "CPU 0 cumulative IPC:" "$base_output_file" | awk '{print $5}')
    
    # Run custom prefetcher and store output
    custom_output_file="$OUTPUT_FOLDER1/${trace_name}_custom.out"

    eval "$CUSTOM_PREFETCHER_EXEC -traces $trace > $custom_output_file"
    custom_ipc=$(grep "CPU 0 cumulative IPC:" "$custom_output_file" | awk '{print $5}')
    
    
    # Calculate speedup ratio and add to speedups array
    if [[ -n $base_ipc && -n $custom_ipc && $base_ipc != "0" ]]; then
        speedup=$(echo "$custom_ipc / $base_ipc" | bc -l)
        speedups+=("$speedup")
        echo "Trace: $trace_name, Base IPC: $base_ipc, Custom IPC: $custom_ipc, Speedup: $speedup"
        # echo "Trace: $trace_name, Base IPC: $base_ipc, Custom IPC: $custom_ipc, Speedup: $speedup" > "results_final1.txt"
    else
        echo "Error calculating IPC for trace: $trace_name"
    fi
done

n=${#speedups[@]}
if [[ $n -gt 0 ]]; then
    product=1
    for speedup in "${speedups[@]}"; do
        product=$(echo "$product * $speedup" | bc -l)
    done
    geomean=$(echo "$product ^ (1/$n)" | bc -l)
    echo "Geometric Mean of Speedup: $geomean"
else
    echo "No valid speedups to calculate geometric mean."
fi
