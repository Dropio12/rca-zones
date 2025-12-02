import os
import PyPDF2

def check_and_remove_pdf(filepath):
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if len(reader.pages) > 0:
                page = reader.pages[0]
                text = page.extract_text()
                # The text we are looking for is "Information for Zone ... is currently unavailable"
                if "Information for Zone" in text and "is currently unavailable" in text:
                    return True
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return False

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    # If the script is in rca-zones, we search in current dir.
    # If it's in parent, we might need to adjust. 
    # Assuming script is placed in rca-zones.
    
    print(f"Scanning {root_dir}...")
    
    files_removed = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(dirpath, filename)
                if check_and_remove_pdf(filepath):
                    print(f"Removing placeholder PDF: {filepath}")
                    try:
                        os.remove(filepath)
                        files_removed += 1
                    except Exception as e:
                        print(f"Failed to remove {filepath}: {e}")

    print(f"Total files removed: {files_removed}")

if __name__ == "__main__":
    main()
