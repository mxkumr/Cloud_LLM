# Function to calculate the sum of a range of numbers
def calculate_sum(start, end):
    return sum(range(start, end + 1))

# Example calculations
sum_1000_to_1000000 = calculate_sum(1000, 1000000)
sum_1000000_to_1000 = calculate_sum(1000000, 1000)  # This will be 0 since start > end

# Since range(start, end+1) with start > end returns empty, we adjust for reverse range
sum_1000000_to_1000_reversed = calculate_sum(1000, 1000000)  # Same as above

# Output results
print("Sum from 1000 to 1000000:", sum_1000_to_1000000)
print("Sum from 1000000 to 1000 (reversed):", sum_1000000_to_1000_reversed)