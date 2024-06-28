import os
import requests
import zipfile
import json
import difflib
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Warning handling
warnings.filterwarnings('ignore', category=NotOpenSSLWarning)

def download_and_unzip_zenodo(zenodo_link, zip_file_path, extract_to="."):
    # Download zip file
    print("Downloading zip file from Zenodo")
    response = requests.get(zenodo_link)
    # Check if the download was successful
    response.raise_for_status()
    with open(zip_file_path, 'wb') as file:
        file.write(response.content)
    print("Download complete.")
    
    # Unzip the downloaded zip file
    if zipfile.is_zipfile(zip_file_path):
        print("File is a valid zip file. Unzipping")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Unzipping complete.")
    else:
        print("The downloaded file is not a valid zip file. Exiting...")
        os.remove(zip_file_path)
        exit(1)

def extract_line_from_jsonl(jsonl_file_path, line_number):
    print(f"Checking line number {line_number} in the JSONL file...")
    with open(jsonl_file_path, 'r') as jsonl_file:
        for current_line_number, line in enumerate(jsonl_file):
            # Adjusting for zero-based index
            if current_line_number == line_number - 1:
                return json.loads(line)
    return None

def compare_functions(extracted_func, github_url):
    response = requests.get(github_url)
    
    if response.status_code == 200:
        github_content = response.text
        
        # Extract the corresponding function
        start_marker = "public final boolean isSupported() {"
        end_marker = "}"
        
        start_index = github_content.find(start_marker)
        if start_index != -1:
            end_index = github_content.find(end_marker, start_index) + len(end_marker)
            github_func = github_content[start_index:end_index].strip()
            
            print("Function from GitHub:\n", github_func)
            
            # Indentation
            extracted_func_normalized = "\n".join([line.strip() for line in extracted_func.strip().splitlines()])
            github_func_normalized = "\n".join([line.strip() for line in github_func.splitlines()])
            
            # Compare functions
            diff = difflib.unified_diff(
                extracted_func_normalized.splitlines(),
                github_func_normalized.splitlines(),
                fromfile='extracted_func',
                tofile='github_func',
                lineterm=''
            )
            
            diff_output = '\n'.join(list(diff))
            if diff_output:
                print("Differences found:\n", diff_output)
            else:
                print("The extracted function matches the mutant in the GitHub repository.")
        else:
            print("The function 'isSupported' was not found in the GitHub file.")
    else:
        print(f"Failed to fetch the file from GitHub. Status code: {response.status_code}")

def main():
    zenodo_link = "https://zenodo.org/records/8388299/files/defect_datasets.zip?download=1"
    zip_file_path = "defect_dataset.zip"
    
    download_and_unzip_zenodo(zenodo_link, zip_file_path)

    jsonl_file_path = "defect/leam-base_all_confirmed_bugs_method_id.jsonl"
    target_line_number = 176288

    # Extract the line from the JSONL
    target_data = extract_line_from_jsonl(jsonl_file_path, target_line_number)
    if target_data:
        print("Target line data:")
        print(json.dumps(target_data, indent=4))
        
        extracted_func = target_data["func"]
        github_url = "https://raw.githubusercontent.com/Intelligent-CAT-Lab/UIUCPlus/leam-base.joda-time.mid-2069.idx-176287.3.mutant/joda-time/src/main/java/org/joda/time/field/BaseDateTimeField.java"
        
        # Compare the extracted function with GitHub
        compare_functions(extracted_func, github_url)
    else:
        print("Specified line not found in the JSONL file.")

if __name__ == "__main__":
    main()
