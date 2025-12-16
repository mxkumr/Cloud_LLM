import io

def copy_bytes(destination, source, num_bytes):
    # Create a BytesIO object to act as a buffer
    buffer = io.BytesIO()
    
    # Write the source data to the buffer
    buffer.write(source[:num_bytes])
    
    # Reset the buffer pointer to the beginning
    buffer.seek(0)
    
    # Read the data from the buffer and copy it to the destination
    destination[:num_bytes] = buffer.read(num_bytes)
    
    # Return the number of bytes copied
    return num_bytes