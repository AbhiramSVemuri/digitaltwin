import os
import csv
import random
from datetime import datetime, timezone
import matplotlib.pyplot as plt

# Constants for power consumption equation
K1 = 200
P_0_ru = 200

def readCSVfile(filename):
    timestamps = []
    utilization_values = []
    ru_node_ids = []

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header row
        ru_node_ids = header[1:]

        # Extract timestamps and utilization values
        for row in reader:
            # Parse the timestamp and convert to timezone-aware datetime in UTC
            timestamp = datetime.fromisoformat(row[0]).replace(tzinfo=timezone.utc)
            timestamps.append(timestamp)

            # Parse utilization values for each RU
            ru_utilization = [float(value) for value in row[1:]]
            utilization_values.append(ru_utilization)

    return timestamps, utilization_values, ru_node_ids

def calculate_power_consumption(utilization_values):
    power_consumption_values = []

    for utilization in utilization_values:
        # Apply the power consumption equation for each RU
        ru_power = [P_0_ru + K1 * u_ru for u_ru in utilization]
        power_consumption_values.append(ru_power)

    return power_consumption_values

def save_power_consumption_to_csv(filename, timestamps, power_consumption_values, ru_node_ids):
    """
    Saves the power consumption values of RUs to a CSV file using RU node IDs as column headers.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Create a header row with RU node IDs
        header = ["Timestamp"] + ru_node_ids
        writer.writerow(header)

        # Write the data rows
        for timestamp, power_values in zip(timestamps, power_consumption_values):
            row = [timestamp.isoformat()] + power_values
            writer.writerow(row)

    print(f"Individual RU power consumption data saved to {filename}")

def save_total_power_to_csv(filename, timestamps, total_power_values):
    """
    Saves the total power consumption values to a CSV file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Create a header row
        header = ["Timestamp", "Total Power Consumption"]
        writer.writerow(header)

        # Write the data rows
        for timestamp, total_power in zip(timestamps, total_power_values):
            row = [timestamp.isoformat(), total_power]
            writer.writerow(row)

    print(f"Total power consumption data saved to {filename}")

def save_and_display_plot(fig, folder, filename):
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    fig.savefig(filepath)
    print(f"Plot saved to {filepath}")
    plt.show()  # Display the plot interactively
    plt.close(fig)  # Close the figure to free memory

def plot_utilization(timestamps, utilization_values, ru_node_ids):
    fig, ax = plt.subplots()
    for i, ru_id in enumerate(ru_node_ids):
        ru_values = [value[i] for value in utilization_values]
        ax.plot(timestamps, ru_values, label=ru_id)

    # Formatting the plot
    ax.set_title("Network Utilization Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Utilization")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

def plot_power_consumption(timestamps, power_consumption_values, ru_node_ids):
    fig, ax = plt.subplots()
    for i, ru_id in enumerate(ru_node_ids):
        ru_values = [value[i] for value in power_consumption_values]
        ax.plot(timestamps, ru_values, label=ru_id)

    # Formatting the plot
    ax.set_title("Power Consumption of Individual RUs")
    ax.set_xlabel("Time")
    ax.set_ylabel("Power Consumption (W)")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

def plot_total_power_consumption(timestamps, total_power_values):
    fig, ax = plt.subplots()
    ax.plot(timestamps, total_power_values, label="Total Power", color='black', linestyle='--', linewidth=2)

    # Formatting the plot
    ax.set_title("Total Power Consumption Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Total Power Consumption (W)")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

def main():
    # Ask the user for the CSV file path
    csv_file_path = input("Enter the CSV file path: ")

    # Read data from the CSV file
    timestamps, utilization_values, ru_node_ids = readCSVfile(csv_file_path)

    print(f"Calculating power consumption for {len(ru_node_ids)} RUs based on CSV data...")

    # Calculate power consumption based on the utilization
    power_consumption_values = calculate_power_consumption(utilization_values)

    # Calculate total power consumption
    total_power_values = [sum(power) for power in power_consumption_values]

    # Save RU power consumption data to a CSV file
    power_csv_folder = "CSVfileOutputs"
    power_csv_filename = os.path.join(power_csv_folder, "ru_power_consumption.csv")
    save_power_consumption_to_csv(power_csv_filename, timestamps, power_consumption_values, ru_node_ids)

    # Save total power consumption data to a CSV file
    total_power_csv_filename = os.path.join(power_csv_folder, "ru_total_power_consumption.csv")
    save_total_power_to_csv(total_power_csv_filename, timestamps, total_power_values)

    # Folder to save plots
    plot_folder = "plotOutputs"

    # Plot and save utilization data
    utilization_fig = plot_utilization(timestamps, utilization_values, ru_node_ids)
    save_and_display_plot(utilization_fig, plot_folder, "ru_utilization_plot.png")

    # Plot and save individual power consumption data
    power_consumption_fig = plot_power_consumption(timestamps, power_consumption_values, ru_node_ids)
    save_and_display_plot(power_consumption_fig, plot_folder, "ru_power_consumption_plot.png")

    # Plot and save total power consumption data
    total_power_fig = plot_total_power_consumption(timestamps, total_power_values)
    save_and_display_plot(total_power_fig, plot_folder, "ru_total_power_consumption_plot.png")

if __name__ == "__main__":
    main()
