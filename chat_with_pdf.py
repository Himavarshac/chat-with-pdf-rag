import fitz  # PyMuPDF

# Function to extract text from a specific page of the PDF
def extract_text_from_page(pdf_path, page_number):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    # Extract text from the specified page (page_number is 0-indexed)
    page = doc.load_page(page_number)
    text = page.get_text("text")
    return text

# Function to extract unemployment data based on degree type from page 2
def extract_unemployment_data(pdf_path, degree_type):
    page_text = extract_text_from_page(pdf_path, page_number=1)  # Page 2 (0-indexed)
    
    # Split the text into lines
    lines = page_text.split('\n')
    
    # Search for the degree type and extract corresponding unemployment data
    data = []
    for line in lines:
        if degree_type.lower() in line.lower():
            data.append(line.strip())
    
    return data

# Function to extract tabular data from page 6
def extract_tabular_data(pdf_path):
    page_text = extract_text_from_page(pdf_path, page_number=5)  # Page 6 (0-indexed)
    
    # Split the text into lines
    lines = page_text.split('\n')
    
    # Extract and return lines that seem to belong to a table (you can further refine this)
    table_data = []
    for line in lines:
        if len(line.strip()) > 0:  # Add logic to filter lines based on the format of the table
            table_data.append(line.strip())
    
    return table_data

# Main function to execute the extraction
def main(pdf_path, degree_type):
    # Step 1: Extract unemployment data for the given degree type
    unemployment_data = extract_unemployment_data(pdf_path, degree_type)
    
    print(f"Unemployment data for degree type '{degree_type}':")
    if unemployment_data:
        for line in unemployment_data:
            print(line)
    else:
        print("No data found for the specified degree type.")
    
    # Step 2: Extract tabular data from page 6
    tabular_data = extract_tabular_data(pdf_path)
    
    print("\nTabular data from page 6:")
    if tabular_data:
        for line in tabular_data:
            print(line)
    else:
        print("No tabular data found on page 6.")

# Run the script
if __name__ == "__main__":
    pdf_path = "G:\\Downloads\\Tables, Charts, and Graphs with Examples from History, Economics, Education, Psychology, Urban Affairs and Everyday Life - 2017-2018.pdf"
    degree_type = "higher national diploma"  # Replace with the degree type you want to search for
    main(pdf_path, degree_type)