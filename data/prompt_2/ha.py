import os
import hashlib

def calculate_file_hash(file_path, hash_algorithm='sha256', buffer_size=65536):
    """
    Calculate the hash of a file using the specified algorithm.
    
    Args:
        file_path (str): Path to the file to hash.
        hash_algorithm (str): Hash algorithm to use (e.g., 'sha256', 'md5').
        buffer_size (int): Size of the buffer to read the file in chunks.
    
    Returns:
        str: The hexadecimal digest of the file's hash.
    """
    # Initialize the hash object with the specified algorithm
    hash_obj = hashlib.new(hash_algorithm)
    
    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Read the file in chunks to handle large files efficiently
        while chunk := file.read(buffer_size):
            hash_obj.update(chunk)
    
    # Return the hexadecimal representation of the hash
    return hash_obj.hexdigest()

# Example usage:
# file_path = "example.txt"
# file_hash = calculate_file_hash(file_path, 'sha256')
# print(f"Hash of {file_path}: {file_hash}")