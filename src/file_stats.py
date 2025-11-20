import os

def count_lines(file_path):
    """
    Counts the number of lines in a given text file.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        int: The number of lines in the file.
        
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return len(lines)

if __name__ == "__main__":
    # Simple manual test
    try:
        path = "README.md"
        count = count_lines(path)
        print(f"File '{path}' has {count} lines.")
    except Exception as e:
        print(f"Error: {e}")

