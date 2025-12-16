# Python code to process and manage data from a list of items (e.g., weather data)
# This example simulates reading, modifying, and saving data using an index-based approach

# Initialize a list to represent data (e.g., weather data)
data = [
    {"city": "Kano", "temperature": 35, "humidity": 60},
    {"city": "Lagos", "temperature": 32, "humidity": 75},
    {"city": "Abuja", "temperature": 28, "humidity": 55},
    {"city": "Port Harcourt", "temperature": 34, "humidity": 80}
]

# Function to display data
def display_data(data_list):
    print("Current data:")
    for idx, item in enumerate(data_list):
        print(f"Index {idx}: {item}")

# Function to update data at a specific index
def update_data(index, new_data):
    if 0 <= index < len(data):
        data[index].update(new_data)
        print(f"Updated index {index} with {new_data}")
    else:
        print("Index out of range!")

# Function to add new data
def add_data(new_item):
    data.append(new_item)
    print(f"Added new item: {new_item}")

# Function to remove data by index
def remove_data(index):
    if 0 <= index < len(data):
        removed = data.pop(index)
        print(f"Removed item: {removed}")
    else:
        print("Index out of range!")

# Example usage
display_data(data)

# Update temperature of Lagos (index 1)
update_data(1, {"temperature": 33})

# Add new city
add_data({"city": "Maiduguri", "temperature": 36, "humidity": 50})

# Remove Kano (index 0)
remove_data(0)

# Final display
display_data(data)