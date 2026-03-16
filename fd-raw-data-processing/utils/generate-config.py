import argparse
from pathlib import Path

def create_input_mapping(directory_to_search, output_filename="output.txt"):
    """
    Traverses a directory looking for *.raw* files and writes them to a formatted text file.
    """
    search_path = Path(directory_to_search)
    
    # Verify the provided directory exists
    if not search_path.exists() or not search_path.is_dir():
        print(f"Error: The path '{directory_to_search}' does not exist or is not a directory.")
        return

    counter = 1
    
    # Open the output file in write mode
    with open(output_filename, 'w', encoding='utf-8') as out_file:
        # .rglob() recursively searches the directory and all subdirectories
        for file_path in search_path.rglob('*.raw*'):
            if file_path.is_file():
                # Write the formatted block
                out_file.write(f"[input-{counter}]\n")
                out_file.write(f"dataOrigin = FV0\n")
                out_file.write(f"dataDescription = RAWDATA\n")
                out_file.write(f"filePath={file_path.absolute()}\n\n")
                
                counter += 1

    print(f"Process complete. {counter - 1} files found and logged to '{output_filename}'.")

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Scan a directory for .raw* files and create an input mapping file.")
    
    # Add a required positional argument for the target directory
    parser.add_argument("directory", help="The target directory to scan (e.g., C:/data or /var/logs)")
    
    # Add an optional argument to allow changing the output filename
    parser.add_argument("-o", "--output", default="output.txt", help="The name of the output file (default: output.txt)")
    
    # Parse the arguments from the command line
    args = parser.parse_args()
    
    # Run the function with the provided arguments
    create_input_mapping(args.directory, args.output)