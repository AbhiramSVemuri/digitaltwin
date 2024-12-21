import csv
from datetime import datetime, timezone
import os
import sys
import matplotlib.pyplot as plt

# Add the path to the digitalTwin directory
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_path not in sys.path:
    sys.path.append(base_path)

try:
    from NetworkConfigurationLoader import parse_oran_topology
    print("Successfully imported NetworkConfigurationLoader.")
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    print("Ensure 'NetworkConfigurationLoader.py' is in the digitalTwin directory.")
    sys.exit(1)

# Filler constants for CU power consumption equation
K_CU = 100
P_0_CU = 200

def read_du_utilization_csv(filename):
    """
    Reads DU utilization values from a CSV file and returns timestamps, utilization values, and DU node IDs.
    """
    timestamps = []
    utilization_values = []
    du_node_ids = []

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header row
        du_node_ids = header[1:]  # Exclude timestamp column

        for row in reader:
            # Parse the timestamp and convert to timezone-aware datetime in UTC
            timestamp = datetime.fromisoformat(row[0]).replace(tzinfo=timezone.utc)
            timestamps.append(timestamp)
            
            # Parse utilization values for each DU
            du_utilization = [float(value) for value in row[1:]]
            utilization_values.append(du_utilization)

    return timestamps, utilization_values, du_node_ids

def calculate_cu_utilizations(network_tree, du_utilizations, du_node_ids):
    """
    Calculates the average utilization for each CU based on the DUs it supports.
    """
    cu_utilizations = {}
    for cu_id, cu_details in network_tree.items():
        if cu_details["type"] == "CU":
            supported_dus = cu_details.get("supports", [])
            if supported_dus:
                indices = [du_node_ids.index(du) for du in supported_dus if du in du_node_ids]
                avg_utilization = sum(du_utilizations[i] for i in indices) / len(indices)
            else:
                avg_utilization = 0.0
            cu_utilizations[cu_id] = round(avg_utilization, 2)
    return cu_utilizations

def calculate_cu_power(cu_utilizations):
    """
    Calculates the power consumption for each CU using a filler equation.
    """
    cu_power = {}
    for cu_id, utilization in cu_utilizations.items():
        power = P_0_CU + K_CU * utilization  # Filler equation
        cu_power[cu_id] = round(power, 2)
    return cu_power

def save_to_csv(filename, headers, data):
    """
    Saves data to a CSV file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Data saved to {filename}")

def plot_and_save(data, timestamps, labels, ylabel, title, filename):
    """
    Plots and saves the data.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(10, 6))

    for label in labels:
        values = [d[label] for d in data]
        plt.plot(timestamps, values, label=label)

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Plot saved as {filename}")
    plt.close()

def main():
    # Input files
    du_csv_file = "C:/Users/abhir/digitalTwin/CSVfileOutputs/du_utilization_data.csv"
    json_file = "C:/Users/abhir/digitalTwin/generatedTopologies/o_ran_network_operational.json"

    # Output directories
    csv_output_dir = "C:/Users/abhir/digitalTwin/CSVfileOutputs"
    plot_output_dir = "C:/Users/abhir/digitalTwin/plotOutputs"

    # Read DU utilization data
    timestamps, du_utilization_values, du_node_ids = read_du_utilization_csv(du_csv_file)

    # Parse the network tree to get CUs and DUs
    _, network_tree = parse_oran_topology(json_file)

    # Initialize lists to store CU utilizations and power values
    cu_utilizations_list = []
    cu_power_list = []

    # Calculate CU utilizations and power consumption for each timestamp
    for i, timestamp in enumerate(timestamps):
        du_utilizations = du_utilization_values[i]
        cu_utilizations = calculate_cu_utilizations(network_tree, du_utilizations, du_node_ids)
        cu_power = calculate_cu_power(cu_utilizations)

        cu_utilizations_list.append(cu_utilizations)
        cu_power_list.append(cu_power)

    # Extract CU node IDs
    cu_nodes = [cu_id for cu_id, details in network_tree.items() if details["type"] == "CU"]

    # Save CU utilizations to CSV and plot
    cu_utilization_filename = os.path.join(csv_output_dir, "cu_utilizations_data.csv")
    save_to_csv(cu_utilization_filename, ["Timestamp"] + cu_nodes, 
                [[timestamps[i].isoformat()] + [cu_utilizations_list[i].get(cu, 0.0) for cu in cu_nodes] for i in range(len(timestamps))])

    cu_utilization_plot_filename = os.path.join(plot_output_dir, "cu_utilizations_plot.png")
    plot_and_save(cu_utilizations_list, timestamps, cu_nodes, 
                  ylabel="Utilization (%)", title="CU Utilizations Over Time", filename=cu_utilization_plot_filename)

    # Save CU power consumption to CSV and plot
    cu_power_filename = os.path.join(csv_output_dir, "cu_power_consumption.csv")
    save_to_csv(cu_power_filename, ["Timestamp"] + cu_nodes, 
                [[timestamps[i].isoformat()] + [cu_power_list[i].get(cu, 0.0) for cu in cu_nodes] for i in range(len(timestamps))])

    cu_power_plot_filename = os.path.join(plot_output_dir, "cu_power_consumption_plot.png")
    plot_and_save(cu_power_list, timestamps, cu_nodes, 
                  ylabel="Power Consumption (W)", title="CU Power Consumption Over Time", filename=cu_power_plot_filename)

    # Calculate total power consumption
    total_power = [[timestamps[i].isoformat(), sum(cu_power_list[i].values())] for i in range(len(timestamps))]

    # Save total power consumption to CSV and plot
    total_power_filename = os.path.join(csv_output_dir, "cu_total_power_consumption.csv")
    save_to_csv(total_power_filename, ["Timestamp", "Total Power"], total_power)

    total_power_plot_filename = os.path.join(plot_output_dir, "cu_total_power_consumption_plot.png")
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, [tp[1] for tp in total_power], label="Total Power", linestyle="--", color="black")
    plt.title("Total Power Consumption Over Time")
    plt.xlabel("Time")
    plt.ylabel("Power Consumption (W)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(total_power_plot_filename)
    print(f"Total power consumption plot saved as {total_power_plot_filename}")
    plt.close()

if __name__ == "__main__":
    main()
