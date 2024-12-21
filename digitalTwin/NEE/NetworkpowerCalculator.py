import csv
import os
import matplotlib.pyplot as plt

def read_csv_file(file_path):
    """
    Reads a CSV file and returns a list of rows.
    """
    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)
            data = [row for row in reader]
        return header, data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None, None

def aggregate_power_consumption(ru_data, du_data, cu_data):
    """
    Aggregates power consumption from RU, DU, and CU power consumption data.
    """
    aggregated_data = []

    for i, ru_row in enumerate(ru_data):
        timestamp = ru_row[0]
        ru_power = sum(map(float, ru_row[1:]))
        du_power = sum(map(float, du_data[i][1:]))
        cu_power = sum(map(float, cu_data[i][1:]))
        total_power = ru_power + du_power + cu_power
        aggregated_data.append([timestamp, round(ru_power, 2), round(du_power, 2), round(cu_power, 2), round(total_power, 2)])

    return aggregated_data

def save_aggregated_data_to_csv(filename, data):
    """
    Saves aggregated power consumption data to a CSV file.
    """
    headers = ["Timestamp", "RU Power", "DU Power", "CU Power", "Total Power"]
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"Aggregated data saved to {filename}")

def plot_aggregated_power(data, output_file, show_figure=False):
    """
    Plots the aggregated power consumption data.
    """
    timestamps = [row[0] for row in data]
    ru_power = [row[1] for row in data]
    du_power = [row[2] for row in data]
    cu_power = [row[3] for row in data]
    total_power = [row[4] for row in data]

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, ru_power, label="RU Power")
    plt.plot(timestamps, du_power, label="DU Power")
    plt.plot(timestamps, cu_power, label="CU Power")
    plt.plot(timestamps, total_power, label="Total Power", linestyle="--", linewidth=2, color="black")

    plt.title("Aggregated Power Consumption Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Power Consumption (W)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file)
    print(f"Aggregated power plot saved to {output_file}")
    if show_figure:
        plt.show()
    plt.close()

def main():
    # Prompt user for input file paths
    ru_file = input("Enter the CSV file path for RU power consumption: ").strip()
    du_file = input("Enter the CSV file path for DU power consumption: ").strip()
    cu_file = input("Enter the CSV file path for CU power consumption: ").strip()

    # Read data from the input files
    ru_header, ru_data = read_csv_file(ru_file)
    du_header, du_data = read_csv_file(du_file)
    cu_header, cu_data = read_csv_file(cu_file)

    if not (ru_data and du_data and cu_data):
        print("Failed to read one or more input files.")
        return

    # Aggregate power consumption data
    aggregated_data = aggregate_power_consumption(ru_data, du_data, cu_data)

    # Save aggregated data to a CSV file
    output_csv = "CSVfileOutputs/aggregated_power_consumption.csv"
    save_aggregated_data_to_csv(output_csv, aggregated_data)

    # Plot aggregated power consumption and display
    output_plot = "plotOutputs/aggregated_power_consumption_plot.png"
    plot_aggregated_power(aggregated_data, output_plot, show_figure=True)

if __name__ == "__main__":
    main()
