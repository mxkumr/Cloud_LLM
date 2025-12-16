def memcpy(destination, source, num_bytes):
    for i in range(num_bytes):
        destination[i] = source[i]

# Example usage with simulated memory
memory = [0] * 1000  # Simulated memory of 1000 bytes

# Copy string "Xin chào" into buffer
message = "Xin chào"
for i, char in enumerate(message):
    memory[0 + i] = ord(char)

# Copy 10 bytes from memory[100] to memory[200]
memcpy(memory[200:210], memory[100:110], 10)

# Copy 5 bytes from memory[300] to memory[400]
memcpy(memory[400:405], memory[300:305], 5)

# Copy 1 byte from memory[500] to memory[600]
memcpy(memory[600:601], memory[500:501], 1)