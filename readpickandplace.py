import csv
import os

# Hard-coded file paths
INPUT_FILE = r"inputdata.csv"
OUTPUT_FILE = r"pcbdata.csv"


def read_pick_and_place(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            csv_reader = csv.reader(infile)
            csv_writer = csv.writer(outfile)
            
            # Skip header lines
            for _ in range(11):
                next(csv_reader)
            
            # Write header
            csv_writer.writerow(['Designator', 'Center-Y(mm)', 'Center-X(mm)', 'Comment', 'Footprint', 'Rotation', 'Description'])
            
            # Read and process component lines
            for row in csv_reader:
                if row and row[0] == 'TopLayer':
                    designator, center_y, center_x, comment, footprint, rotation, description = row[1:8]
                    # Replace comma with dot in coordinates
                    center_y = center_y.replace(',', '.')
                    center_x = center_x.replace(',', '.')
                    # Ensure µ is correctly encoded
                    comment = comment.replace('µ', '\u00B5')
                    description = description.replace('µ', '\u00B5')
                    csv_writer.writerow([designator, center_y, center_x, comment, footprint, rotation, description])
        
        print(f"Data has been successfully written to {output_file}")
        return True
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return False

if __name__ == "__main__":
    print("Current directory:", os.getcwd())
    print("Files in current directory:")
    for file in os.listdir():
        print(f"  {file}")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: File '{INPUT_FILE}' not found.")
    else:
        if read_pick_and_place():
            print("CSV file created successfully.")
            print("Files in current directory after processing:")
            for file in os.listdir():
                print(f"  {file}")
        else:
            print("Failed to create CSV file.")