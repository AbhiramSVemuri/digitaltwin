import os
import csv
from datetime import datetime, timedelta
import random
from NetworkConfigurationLoader import parse_oran_topology  # Import the parser function

def get_start_of_day():
    # Get the current date's midnight (start of the day)
    current_time = datetime.now()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_of_day

def generate_data_points(num_intervals, num_rus):
    data_points = []
    start_time = get_start_of_day()

    # Define baseline utilizations for each hour (U_ru,b)
    baseline_utilizations = [
        0.25, 0.22, 0.15, 0.12, 0.11, 0.14, 0.22, 0.36, 0.48, 0.58,
        0.63, 0.67, 0.76, 0.87, 0.9, 0.84, 0.73, 0.65, 0.52, 0.46,
        0.37, 0.35, 0.33, 0.29
    ]

    # Generate utilization values for each hour and RU
    for i in range(num_intervals):
        timestamp = start_time + timedelta(hours=i)
        current_hour = timestamp.hour

        # Baseline utilization for the current hour
        U_ru_b = baseline_utilizations[current_hour]

        # Generate utilization values using the equation
        ru_utilizations = [
            round(max(min(U_ru_b + (0.5 - random.uniform(0, 1)) * 0.7, 1), 0), 2)  # Ensure values are between 0 and 1
            for _ in range(num_rus)
        ]
        data_points.append([timestamp] + ru_utilizations)
    
    return data_points


def save_to_csv(filename, data_points, ru_node_ids):
    # Ensure the folder exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save the generated data to a CSV file
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Create a header with the node IDs as column names
        header = ["Timestamp"] + ru_node_ids
        writer.writerow(header)  # Write header
        # Write data rows
        for row in data_points:
            # Convert timestamp to ISO format string
            row[0] = row[0].isoformat()
            writer.writerow(row)

# Main execution
def main():
    json_file = "C:/Users/abhir/digitalTwin/generatedTopologies/o_ran_network_operational.json"  # Replace with your JSON file path
    try:
        # Parse the network tree to get RUs
        nodes, network_tree = parse_oran_topology(json_file)

        # Extract RU nodes and count
        ru_nodes = [node_id for node_id, details in network_tree.items() if details["type"] == "RU"]
        num_rus = len(ru_nodes)

        print(f"Number of RUs detected: {num_rus}")

        # Parameters for data generation
        num_intervals = 24  # 24 intervals for a full day (hourly)

        # Generate data points
        data_points = generate_data_points(num_intervals, num_rus)

        # Save to CSV in the desired folder
        filename = os.path.join("C:/Users/abhir/digitalTwin/CSVfileOutputs", "ru_utilization_data.csv")
        save_to_csv(filename, data_points, ru_nodes)

        print(f"Data saved to {filename}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
