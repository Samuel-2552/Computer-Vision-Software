import os
import ctypes
import subprocess
import sys
import time

# Path to the file storing the installation date
file_path = 'C:\\ProgramData\\ICVS\\installation.txt'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def set_file_permissions():
    try:
        # Run icacls command to set permissions
        command = f"icacls {file_path} /inheritance:r /grant:r *S-1-1-0:(R)"
        subprocess.run(command, shell=True, check=True)

        print("File permissions set successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while setting file permissions: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def create_file_with_timestamp():
    try:
        # Get current timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the file with timestamp
        with open(file_path, 'w') as file:
            file.write(timestamp)

        print(f"File created successfully with timestamp: {timestamp}")
    except Exception as e:
        print("Error occurred while creating the file:", e)

def print_file_content():
    try:
        # Read and print the content of the file
        with open(file_path, 'r') as file:
            content = file.read()
            print(f"File content:\n{content}")
    except Exception as e:
        print("Error occurred while reading the file:", e)

if is_admin():
    # Call the function to create the file with timestamp
    create_file_with_timestamp()

    # Call the function to set file permissions
    set_file_permissions()

    print_file_content()

else:
    elevate()
