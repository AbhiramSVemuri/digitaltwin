from collections import defaultdict
import json

def parse_oran_topology(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Parse networks
    networks = data.get("ietf-network:networks", {}).get("network", [])
    if not networks:
        raise ValueError("No networks found in the JSON file.")

    # Initialize storage for RU, DU, CU nodes and relationships
    nodes = {"RU": [], "DU": [], "CU": []}
    network_tree = defaultdict(lambda: {"type": None, "supports": []})

    # Collect nodes and links
    for network in networks:
        nodes_data = network.get("node", [])
        links_data = network.get("ietf-network-topology:link", [])

        # Process nodes
        for node in nodes_data:
            node_id = node.get("node-id", "")
            node_type = node.get("o-ran-sc-network:type", "")

            if node_id.startswith("O-RAN-RU"):
                nodes["RU"].append(node_id)
                network_tree[node_id]["type"] = "RU"
            elif node_id.startswith("O-RAN-DU"):
                nodes["DU"].append(node_id)
                network_tree[node_id]["type"] = "DU"
            elif node_id.startswith("O-RAN-CU"):
                nodes["CU"].append(node_id)
                network_tree[node_id]["type"] = "CU"

        # Process links
        for link in links_data:
            source_node = link.get("source", {}).get("source-node", "")
            dest_node = link.get("destination", {}).get("dest-node", "")

            if not source_node or not dest_node:
                continue  # Skip invalid links

            # Determine the type of source and destination nodes
            source_type = network_tree[source_node]["type"]
            dest_type = network_tree[dest_node]["type"]

            # Correct the relationship direction
            if source_type == "DU" and dest_type == "RU":
                # DU supports RU (correct direction)
                network_tree[source_node]["supports"].append(dest_node)
            elif source_type == "RU" and dest_type == "DU":
                # Reverse the direction: DU should support RU
                network_tree[dest_node]["supports"].append(source_node)
            elif source_type == "CU" and dest_type == "DU":
                # CU supports DU (correct direction)
                network_tree[source_node]["supports"].append(dest_node)
            elif source_type == "DU" and dest_type == "CU":
                # Reverse the direction: CU should support DU
                network_tree[dest_node]["supports"].append(source_node)

    # Remove duplicates in the supports lists
    for node_id, relationships in network_tree.items():
        relationships["supports"] = list(set(relationships["supports"]))
    
    return nodes, network_tree

# Example Usage
json_file = "C:/Users/abhir/digitalTwin/generatedTopologies/o_ran_network_operational.json"
try:
    nodes, network_tree = parse_oran_topology(json_file)

    print("Nodes:")
    print(json.dumps(nodes, indent=2))

    print("\nNetwork Tree:")
    for node_id, details in network_tree.items():
        if details["type"] in ["RU", "DU", "CU"]:  # Only print RU, DU, and CU nodes
            print(f"Node ID: {node_id}")
            print(f"  Type: {details['type']}")
            print(f"  Supports: {details['supports']}")
            print()

except ValueError as e:
    print(e)
