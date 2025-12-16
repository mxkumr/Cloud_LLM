# Python code to simulate the described scenario
def calculate_usage():
    # Initial values
    initial_capacity = 1200
    used_capacity = 1000
    additional_usage = 1000
    remaining_capacity = initial_capacity - used_capacity

    # Check if additional usage exceeds remaining capacity
    if additional_usage <= remaining_capacity:
        total_used = used_capacity + additional_usage
        remaining_after = remaining_capacity - additional_usage
    else:
        total_used = initial_capacity
        remaining_after = 0

    return total_used, remaining_after

# Execute the function
total_used, remaining = calculate_usage()
print(f"Total used: {total_used}, Remaining: {remaining}")