import os


"""
Given 2 directories a and b
Delete all the files from b that appear in a
"""

def delete_files_in_directory(directory, filename_list):

    with open(filename_list, 'r') as f:
        filenames_to_delete = set(f.read().splitlines())

    for filename in filenames_to_delete:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            os.remove(file_path)



directory = r"C:\Users\dunca\Desktop\b"
filename_list_path = "logs.txt"
delete_files_in_directory(directory, filename_list_path)