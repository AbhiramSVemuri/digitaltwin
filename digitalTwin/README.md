# Digital Twin for Wireless O-RAN Network Energy Consumption by Abhiram S. Vemuri

## Installation/Setup

This is a python program with external dependencies. Please install the necessary dependencies for these modules/libraries through the terminal:

- JSON Module 
- OS Module
- CSV Module
- Datetime Module
- Matplotlib Library


Use the the latest Python application (version 3.12.4) and create virtual environment for running
sny scripts in this directory.

# Steps 

1) Navigate to the NetworkConfigurationLoader.py file. Enter the file path for the JSON file in the script when asked for. This will output a Nodes and Network Tree list to be imported later into other modules.

2) Navigate to the csvFileGenerator.py (CSVFG). In line 60 replace the file path with the file path to JSON topology you want to parse. An RU utilizations csv file (ru_utilization_data.csv) will be generated in the CSVfileOutputs folder for each RU detected in the topology file.

3) Navigate to RU power calculator (RUpowerCalculator.py) in the NEE folder. Run the script and when prompted to do so, copy/enter the csv file path for to the ru_utilizations_data.csv file. This will output three plots in the plotOutputs folder (Individual RU power consumptions: ru_power_consumption_plot.png, Total RU power consumptions: ru_total_power_consumption_plot.png, and RU utilizations: ru_utilization_plot.png) and two csv files in the CSVfileOutputs folder (Individual RU power consumptions: ru_power_consumption.csv, Total RU power consumptions: ru_total_power_consumption.csv). 

4) Navigate to the DU power calculator (DUpowercalculator.py) in the NEE folder. Enter the correct JSON topology file to be parsed in line 152. Then run the script and when prompted to do so, enter the csv file path to the RU utilizations data (ru_utilization_data.csv). This will output three more plots in the plotOutputs folder (Individual DU power consumptions: du_power_consumption_plot.png, Total DU power consumptions: du_total_power_consumption_plot.png, and DU utilizations: du_utilization_plot.png) and three more CSV files in the CSVfileOutputs folder (Individual DU power consumptions: du_power_consumption_data.csv, Total DU power consumptions: du_total_power_consumption_data.csv, and DU utilizations: du_utilizations_data).

5) Navigate to the CU power calculator (CUpowercalculator.py) in the NEE folder. In line 109, enter the CSV file path to the DU utilizations (du_utilization_data.py) and in line 110 enter the JSON topology path for parsing. Then run the script. This will output three more plots in the plotOutputs folder (Individual CU power consumptions: cu_power_consumption_plot.png, Total CU power consumptions: cu_total_power_consumption_plot.png, and CU utilizations: cu_utilizations_plot.png) and three more CSV files in the CSVfileOutputs folder (Individual CU power consumptions: cu_power_consumption.csv, Total CU power consumptions: cu_total_power_consumption.csv, and CU utilizations: cu_utilizations_data.csv).

6) Navigate to the Network Power Calculator (NetworkpowerCalculator.py) in the NEE folder. When prompted to do so, enter the total power consumption CSV file paths of the RUs, DUs, and CUs respectively. The total power consumption graph and its CSV file will be generated (saved as aggregated_power_consumption.csv and aggregated_power_consumption_plot.png) in the CSVfileOutputs folder and in the plotOutputs folder respectively. 

7) To rerun the scripts for another JSON topology, simply change the JSON file path to the new topology and repeat steps 1-6. The output files will automatically get overwritten. Make sure to save them in another folder before rerunning the code. 