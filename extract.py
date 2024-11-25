import os
import re

# Directories to search
directories = ["outputs", "outputsp"]

# Output file for IPC values
output_file = "ipc_comparison.txt"

# Regex pattern to match IPC values
ipc_pattern = re.compile(r"CPU 0 cumulative IPC:\s+([\d\.]+)")

# Dictionary to store IPC values for each trace
ipc_values = {}

for directory in directories:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".out"):
                trace_name = file.rsplit("_", 1)[0]  # Extract trace name without suffix
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                    match = ipc_pattern.search(content)
                    if match:
                        ipc = match.group(1)
                        if trace_name not in ipc_values:
                            ipc_values[trace_name] = {"base": None, "custom": None}
                        if file.endswith("_base.out"):
                            ipc_values[trace_name]["base"] = ipc
                        elif file.endswith("_custom.out"):
                            ipc_values[trace_name]["custom"] = ipc

# Write the IPC values to the output file
with open(output_file, "w") as f:
    f.write("Trace Name\tBase IPC\tCustom IPC\n")
    for trace, values in sorted(ipc_values.items()):
        base_ipc = values["base"] or "N/A"
        custom_ipc = values["custom"] or "N/A"
        f.write(f"{trace}\t{base_ipc}\t{custom_ipc}\n")

print(f"IPC comparison saved to {output_file}")
