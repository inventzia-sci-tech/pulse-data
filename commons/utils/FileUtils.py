import subprocess
import os

def extract_with_7zip(archive_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    # Command to extract with 7zip
    command = f'7z x "{archive_path}" -o"{output_folder}"'
    try:
        # Run the command using subprocess
        subprocess.run(command, shell=True, check=True)
        print(f"Extraction successful to {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Extraction failed with error: {e}")
        raise e