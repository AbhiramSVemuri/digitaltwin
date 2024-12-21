import os
import csv
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import sys

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

# Constants for DU power consumption equation
P_0_DU = 200
K1_DU = 200
K2_DU = 20

def read_ru_utilization_csv(filename):
    """
    Reads RU utilization values from a CSV file.
    """
    timestamps = []
    utilization_values = []
    ru_node_ids = []

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read header row
        ru_node_ids = header[1:]  # Exclude timestamp column

        for row in reader:
            # Convert timestamp to a timezone-aware datetime
            timestamp = datetime.fromisoformat(row[0]).replace(tzinfo=timezone.utc)
            ru_utilizations = [float(value) for value in row[1:]]
            timestamps.append(timestamp)
            utilization_values.append(ru_utilizations)

    return timestamps, utilization_values, ru_node_ids

def calculate_du_utilizations(network_tree, ru_utilizations, ru_node_ids):
    """
    Calculates the average utilization for each DU based on its supported RUs.
    """
    du_utilizations = {}
    for node_id, details in network_tree.items():
        if details["type"] == "DU":
            supported_rus = details.get("supports", [])
            if supported_rus:
                indices = [ru_node_ids.index(ru) for ru in supported_rus if ru in ru_node_ids]
                avg_utilization = sum(ru_utilizations[i] for i in indices) / len(indices)
            else:
                avg_utilization = 0.0
            du_utilizations[node_id] = round(avg_utilization, 2)
    return du_utilizations

def calculate_du_power(du_utilizations, network_tree):
    """
    Calculates DU power consumption based on utilization.
    """
    du_power = {}
    for node_id, utilization in du_utilizations.items():
        num_rus = len(network_tree[node_id].get("supports", []))
        power = P_0_DU + K1_DU * utilization + K2_DU * num_rus
        du_power[node_id] = round(power, 2)
    return du_power

def save_to_csv(filename, data_points, node_ids):
    """
    Saves the generated data to a CSV file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ["Timestamp"] + node_ids
        writer.writerow(header)

        for row in data_points:
            row[0] = row[0].isoformat()  # Convert timestamp to ISO format string
            writer.writerow(row)

def save_total_power_to_csv(filename, timestamps, total_power_values):
    """
    Saves total power consumption of all DUs to a CSV file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Total Power Consumption (W)"])

        for timestamp, total_power in zip(timestamps, total_power_values):
            writer.writerow([timestamp.isoformat(), total_power])

def plot_data(timestamps, data_list, node_ids, ylabel, title, filename):
    """
    Plots and saves data for DU utilizations or power consumption.
    """
    plt.figure(figsize=(10, 6))

    for i, node_id in enumerate(node_ids):
        values = [data[i + 1] for data in data_list]  # Skip timestamp in data row
        plt.plot(timestamps, values, label=node_id)

    plt.title(title)
    plt.xlabel("Timestamp")
    plt.ylabel(ylabel)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(filename)
    plt.show()
    plt.close()
    print(f"Plot saved to {filename}")

def plot_total_power(timestamps, total_power_values, ylabel, title, filename):
    """
    Plots and saves the total power consumption of all DUs.
    """
    plt.figure(figsize=(10, 6))

    plt.plot(timestamps, total_power_values, label="Total Power", linestyle="--", color="red")

    plt.title(title)
    plt.xlabel("Timestamp")
    plt.ylabel(ylabel)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(filename)
    plt.show()
    plt.close()
    print(f"Plot saved to {filename}")

# Main execution
def main():
    ru_csv_file = input("Enter the RU utilization CSV file path: ").strip()

    try:
        # Directly fetch the network tree from the NetworkConfigurationLoader
        _, network_tree = parse_oran_topology("C:/Users/abhir/digitalTwin/generatedTopologies/o_ran_network_operational.json")

        # Parse RU utilization data
        timestamps, ru_utilization_values, ru_node_ids = read_ru_utilization_csv(ru_csv_file)

        # Initialize lists to store DU utilization and power values
        du_utilizations_list = []
        du_power_list = []
        total_power_values = []

        # Calculate DU utilization and power consumption for each timestamp
        for i, timestamp in enumerate(timestamps):
            ru_utilizations = ru_utilization_values[i]
            du_utilizations = calculate_du_utilizations(network_tree, ru_utilizations, ru_node_ids)
            du_power = calculate_du_power(du_utilizations, network_tree)

            du_utilizations_list.append([timestamp] + list(du_utilizations.values()))
            du_power_list.append([timestamp] + list(du_power.values()))

            # Calculate total power for all DUs at this timestamp
            total_power = sum(du_power.values())
            total_power_values.append(total_power)

        # Extract DU node IDs
        du_nodes = [node_id for node_id, details in network_tree.items() if details["type"] == "DU"]

        # Save DU utilization data to CSV
        du_utilization_filename = os.path.join("CSVfileOutputs", "du_utilization_data.csv")
        save_to_csv(du_utilization_filename, du_utilizations_list, du_nodes)
        print(f"DU utilization data saved to {du_utilization_filename}")

        # Save DU power consumption data to CSV
        du_power_filename = os.path.join("CSVfileOutputs", "du_power_consumption_data.csv")
        save_to_csv(du_power_filename, du_power_list, du_nodes)
        print(f"DU power consumption data saved to {du_power_filename}")

        # Save total power consumption data to CSV
        total_power_filename = os.path.join("CSVfileOutputs", "du_total_power_consumption_data.csv")
        save_total_power_to_csv(total_power_filename, timestamps, total_power_values)
        print(f"Total DU power consumption data saved to {total_power_filename}")

        # Plot DU utilization and save
        utilization_plot_filename = os.path.join("plotOutputs", "du_utilizations_plot.png")
        plot_data(
            timestamps, du_utilizations_list, du_nodes,
            ylabel="Utilization", title="DU Utilizations Over Time",
            filename=utilization_plot_filename
        )

        # Plot DU power consumption and save
        power_plot_filename = os.path.join("plotOutputs", "du_power_consumption_plot.png")
        plot_data(
            timestamps, du_power_list, du_nodes,
            ylabel="Power Consumption (W)", title="DU Power Consumption Over Time",
            filename=power_plot_filename
        )

        # Plot total power consumption and save
        total_power_plot_filename = os.path.join("plotOutputs", "du_total_power_consumption_plot.png")
        plot_total_power(
            timestamps, total_power_values,
            ylabel="Total Power Consumption (W)", title="Total DU Power Consumption Over Time",
            filename=total_power_plot_filename
        )

    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()