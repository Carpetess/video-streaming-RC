def get_bits_16_to_31(num, total_bits=128):
    # Shift the number right to move bits 16-31 to the least significant position
    return (num >> (total_bits - 32)) & 0xFFFF

# Example usage
header = 0x123456789ABCDEF123456789ABCDEF12  # A 128-bit number example
bits_16_to_31 = get_bits_16_to_31(header)
print(hex(bits_16_to_31))  # Print in hex format for better readability
